export type HookEventType = 'beforeRequestHook' | 'afterRequestHook';

export interface PluginRequestContext {
  json?: Record<string, any> | null;
  text?: string | null;
  isStreamingRequest?: boolean;
  isTransformed?: boolean;
}

export interface PluginResponseContext {
  json?: Record<string, any> | null;
  text?: string | null;
  statusCode?: number | null;
  isTransformed?: boolean;
}

export interface PluginContext {
  request?: PluginRequestContext;
  response?: PluginResponseContext;
  credentials?: Record<string, any> | null;
  metadata?: Record<string, any> | null;
  provider?: string | null;
}

export interface PluginParameters {
  [key: string]: any;
}

export interface PluginResult {
  error: any;
  verdict: boolean;
  data: any;
  transformedData?: Record<string, any>;
  transformed?: boolean;
}

export type PluginHandler = (
  context: PluginContext,
  parameters: PluginParameters,
  eventType: HookEventType,
) => Promise<PluginResult>;
