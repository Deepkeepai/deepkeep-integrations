import {
  HookEventType,
  PluginContext,
  PluginHandler,
  PluginParameters,
} from '../types';

type DeepKeepVerbosityItem = {
  guardrail_name?: string;
  risk_level?: string;
  details?: {
    guardrail_action?: string;
    modified?: Array<{ role?: string; content?: string }>;
    detector_output?: Array<Record<string, any>>;
  };
};

const ACTION_PRIORITY: Record<string, number> = {
  block: 4,
  redact: 3,
  modify: 2,
  alert: 1,
};

function deepClone<T>(value: T): T {
  return value === null || value === undefined
    ? value
    : JSON.parse(JSON.stringify(value));
}

function getBool(value: any, defaultValue: boolean): boolean {
  if (typeof value === 'boolean') return value;
  return defaultValue;
}

function getNumber(value: any, defaultValue: number): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  return defaultValue;
}

function getString(value: any): string {
  return typeof value === 'string' ? value : '';
}

function getFirewallId(parameters: PluginParameters, eventType: HookEventType): string {
  const perHook =
    eventType === 'beforeRequestHook'
      ? getString(parameters.inputFirewallId)
      : getString(parameters.outputFirewallId);

  return perHook || getString(parameters.firewallId);
}

function getTextToModerate(context: PluginContext, eventType: HookEventType): string {
  if (eventType === 'beforeRequestHook') {
    return getString(context.request?.text);
  }

  return getString(context.response?.text);
}

function getDeepKeepEndpoint(parameters: PluginParameters, eventType: HookEventType): string {
  const baseUrl = getString(parameters.apiBaseUrl).replace(/\/$/, '');
  const endpoint = eventType === 'beforeRequestHook' ? 'pre' : 'post';
  return `${baseUrl}/api/v3/openai/moderations/${endpoint}`;
}

function getAuthHeaders(context: PluginContext): Record<string, string> {
  const credentials = context.credentials || {};
  const headers: Record<string, string> = {};

  if (typeof credentials.bearerToken === 'string' && credentials.bearerToken) {
    headers.Authorization = `Bearer ${credentials.bearerToken}`;
  } else if (typeof credentials.apiKey === 'string' && credentials.apiKey) {
    headers['X-API-Key'] = credentials.apiKey;
  }

  return headers;
}

function extractModifiedText(resp: any): string {
  const candidates = [
    resp?.modified_output,
    resp?.modified_input,
    resp?.content,
    resp?.text,
    resp?.output,
    resp?.input,
  ];

  for (const candidate of candidates) {
    if (typeof candidate === 'string' && candidate) {
      return candidate;
    }
  }

  const verbosity: DeepKeepVerbosityItem[] = Array.isArray(resp?.verbosity)
    ? resp.verbosity
    : [];

  for (const item of verbosity) {
    const modified = item.details?.modified;
    if (Array.isArray(modified)) {
      for (const entry of modified) {
        if (typeof entry?.content === 'string' && entry.content) {
          return entry.content;
        }
      }
    }
  }

  return '';
}

function pickAction(resp: any): { action: string; item: DeepKeepVerbosityItem | null } {
  const verbosity: DeepKeepVerbosityItem[] = Array.isArray(resp?.verbosity)
    ? resp.verbosity
    : [];

  let bestAction = 'block';
  let bestScore = 0;
  let bestItem: DeepKeepVerbosityItem | null = null;

  for (const item of verbosity) {
    const action = String(item?.details?.guardrail_action || 'alert').toLowerCase();
    const score = ACTION_PRIORITY[action] || 1;

    if (score > bestScore) {
      bestScore = score;
      bestAction = action;
      bestItem = item;
    }
  }

  return { action: bestAction, item: bestItem };
}

function transformRequestJson(original: any, redactedText: string): any {
  const requestJson = deepClone(original) || {};

  if (Array.isArray(requestJson.messages)) {
    for (let i = requestJson.messages.length - 1; i >= 0; i -= 1) {
      const message = requestJson.messages[i];
      if (message && typeof message === 'object' && message.role !== 'system') {
        message.content = redactedText;
        return requestJson;
      }
    }
  }

  if (typeof requestJson.prompt === 'string') {
    requestJson.prompt = redactedText;
    return requestJson;
  }

  if (typeof requestJson.input === 'string') {
    requestJson.input = redactedText;
    return requestJson;
  }

  requestJson.text = redactedText;
  return requestJson;
}

function transformResponseJson(original: any, redactedText: string): any {
  const responseJson = deepClone(original) || {};

  if (Array.isArray(responseJson.choices)) {
    for (const choice of responseJson.choices) {
      if (choice?.message && typeof choice.message === 'object') {
        choice.message.content = redactedText;
      }
      if (typeof choice?.text === 'string') {
        choice.text = redactedText;
      }
    }
  } else if (typeof responseJson.text === 'string') {
    responseJson.text = redactedText;
  }

  return responseJson;
}

async function callDeepKeep(
  context: PluginContext,
  parameters: PluginParameters,
  eventType: HookEventType,
  text: string,
): Promise<any> {
  const endpoint = getDeepKeepEndpoint(parameters, eventType);
  const payloadKey = eventType === 'beforeRequestHook' ? 'input' : 'output';
  const body: Record<string, any> = {
    model: getFirewallId(parameters, eventType),
    [payloadKey]: text,
  };

  const chatId = getString(parameters.chatId);
  const title = getString(parameters.title);

  if (chatId) body.chat = chatId;
  if (title) body.title = title;

  const controller = new AbortController();
  const timeoutMs = getNumber(parameters.timeoutMs, 10000);
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(context),
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    const responseText = await response.text();
    let parsed: any = null;

    try {
      parsed = responseText ? JSON.parse(responseText) : null;
    } catch {
      parsed = responseText;
    }

    if (!response.ok) {
      throw new Error(`DeepKeep returned HTTP ${response.status}`);
    }

    return parsed;
  } finally {
    clearTimeout(timeout);
  }
}

function buildResult(resp: any, eventType: HookEventType, context: PluginContext): any {
  const flagged = Boolean(resp?.flagged);
  const { action } = flagged ? pickAction(resp) : { action: 'alert' };
  const modifiedText = extractModifiedText(resp);

  const result = {
    request_id: resp?.request_id,
    firewall_name: resp?.firewall_name,
    risk_level: resp?.risk_level,
    action,
    flagged,
    verbosity: resp?.verbosity || [],
    modified_text: modifiedText || null,
    eventType,
  };

  const transformedData: Record<string, any> = {
    request: { json: null, text: null },
    response: { json: null, text: null },
  };

  let transformed = false;

  if (flagged && (action === 'redact' || action === 'modify') && modifiedText) {
    if (eventType === 'beforeRequestHook') {
      transformedData.request.json = transformRequestJson(context.request?.json, modifiedText);
      transformedData.request.text = modifiedText;
    } else {
      transformedData.response.json = transformResponseJson(context.response?.json, modifiedText);
      transformedData.response.text = modifiedText;
    }

    transformed = true;
  }

  return { result, transformedData, transformed };
}

export const handler: PluginHandler = async (
  context: PluginContext,
  parameters: PluginParameters,
  eventType: HookEventType,
) => {
  let error = null;
  let verdict = true;
  let data: any = null;
  const transformedData: Record<string, any> = {
    request: { json: null, text: null },
    response: { json: null, text: null },
  };
  let transformed = false;

  try {
    const textToCheck = getTextToModerate(context, eventType);

    if (!textToCheck) {
      return { error: null, verdict: true, data: null, transformedData, transformed };
    }

    const moderationResponse = await callDeepKeep(
      context,
      parameters,
      eventType,
      textToCheck,
    );

    const outcome = buildResult(moderationResponse, eventType, context);

    verdict = !(outcome.result.flagged && outcome.result.action === 'block');

    data = outcome.result;
    if (outcome.transformed) {
      transformed = true;
      transformedData.request = outcome.transformedData.request;
      transformedData.response = outcome.transformedData.response;
    }

  } catch (e: any) {
    error = e;
    const failOpen = getBool(parameters.failOpen, true);
    verdict = failOpen;
    data = {
      error: e?.message || String(e),
      failOpen,
    };
  }

  return { error, verdict, data, transformedData, transformed };
};
