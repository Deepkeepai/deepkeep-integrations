# DeepKeep LiteLLM Guardrail

This repo contains a LiteLLM `CustomGuardrail` adapter for DeepKeep.

## What it does

- `pre_call` maps to `POST /api/v3/openai/moderations/pre`
- `post_call` maps to `POST /api/v3/openai/moderations/post`

## Files

- `deepkeep_guardrail.py` - the custom guardrail class
- `config.example.yaml` - LiteLLM config example

## Environment variables

- `DEEPKEEP_API_BASE`
- `DEEPKEEP_API_KEY`
- `DEEPKEEP_FIREWALL_ID`
- Optional: `DEEPKEEP_BEARER_TOKEN`, `DEEPKEEP_CHAT`, `DEEPKEEP_TITLE`

## LiteLLM config

```yaml
guardrails:
  - guardrail_name: deepkeep-pre
    litellm_params:
      guardrail: deepkeep_guardrail.DeepKeepGuardrail
      mode: pre_call
      api_base: os.environ/DEEPKEEP_API_BASE
      api_key: os.environ/DEEPKEEP_API_KEY
      firewall_id: os.environ/DEEPKEEP_FIREWALL_ID

  - guardrail_name: deepkeep-post
    litellm_params:
      guardrail: deepkeep_guardrail.DeepKeepGuardrail
      mode: post_call
      api_base: os.environ/DEEPKEEP_API_BASE
      api_key: os.environ/DEEPKEEP_API_KEY
      firewall_id: os.environ/DEEPKEEP_FIREWALL_ID
```

## Notes

- `pre_call` is the right place to moderate the prompt before the LLM call.
- `post_call` is the right place to moderate the LLM response.
- For streaming responses, LiteLLM post-call guardrails are audit-oriented after delivery.
