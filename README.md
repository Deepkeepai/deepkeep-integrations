# DeepKeep agentgateway Guardrail Webhook

This service adapts agentgateway guardrail webhook calls to DeepKeep's OpenAI-compatible moderation endpoints.

It exposes the webhook paths expected by agentgateway:

- `POST /request` calls DeepKeep `/api/v3/openai/moderations/pre`
- `POST /response` calls DeepKeep `/api/v3/openai/moderations/post`

## Configuration

Set these environment variables:

- `DEEPKEEP_BASE_URL`: Base URL for your DeepKeep instance, without a trailing slash
- `DEEPKEEP_API_KEY`: DeepKeep API key sent as `X-API-Key`
- `DEEPKEEP_MODEL`: DeepKeep firewall ID sent as the OpenAI-compatible `model`
- `DEEPKEEP_TITLE`: Optional title sent to DeepKeep
- `DEEPKEEP_CHAT`: Optional chat identifier/context sent to DeepKeep
- `DEEPKEEP_TIMEOUT`: Optional request timeout in seconds, default `30`

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DEEPKEEP_BASE_URL=https://deepkeep.example
set DEEPKEEP_API_KEY=dk_...
set DEEPKEEP_MODEL=your-firewall-id
uvicorn deepkeep_webhook:app --host 0.0.0.0 --port 8000
```

## Run With Docker

```bash
docker build -t agentgateway-deepkeep-webhook .
docker run --rm -p 8000:8000 \
  -e DEEPKEEP_BASE_URL=https://deepkeep.example \
  -e DEEPKEEP_API_KEY=dk_... \
  -e DEEPKEEP_MODEL=your-firewall-id \
  agentgateway-deepkeep-webhook
```

Or use Docker Compose:

```bash
set DEEPKEEP_BASE_URL=https://deepkeep.example
set DEEPKEEP_API_KEY=dk_...
set DEEPKEEP_MODEL=your-firewall-id
docker compose up --build
```

## Action Mapping

For `POST /request`:

- DeepKeep `block` returns agentgateway `RejectAction` with status `403`
- DeepKeep `redact` or `modify` returns `MaskAction` when DeepKeep returns modified content
- DeepKeep `alert` or no action returns `PassAction`
- Unsupported DeepKeep actions fail closed with `RejectAction`

For `POST /response`:

- DeepKeep `redact` or `modify` returns `MaskAction` when DeepKeep returns modified content
- DeepKeep `alert` or no action returns `PassAction`
- DeepKeep `block` returns `MaskAction` with response content cleared because the agentgateway response webhook schema allows pass/mask only
- Unsupported DeepKeep actions fail closed by clearing response content with `MaskAction`

## agentgateway Configuration Example

Configure an agentgateway webhook prompt guard to point at this service. The webhook URL should use the service root; agentgateway calls `/request` and `/response` on that root.

```yaml
promptGuard:
  request:
    webhook:
      url: http://deepkeep-webhook.default.svc.cluster.local:8000
  response:
    webhook:
      url: http://deepkeep-webhook.default.svc.cluster.local:8000
```

Adjust the resource shape to match the agentgateway mode you are using. The webhook payload contract is the standard guardrail webhook API: prompt requests contain `body.messages`, and response checks contain `body.choices`.

More examples are available in `examples/standalone` and `examples/kubernetes`.

## Container Image

The example manifests use this image name:

```text
ghcr.io/deepkeepai/agentgateway-deepkeep-webhook:latest
```

If you publish the image under another organization, update `examples/kubernetes/deployment.yaml` accordingly.

## Test Requests

```bash
curl -s http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{"body":{"messages":[{"role":"user","content":"hello"}]}}'
```

```bash
curl -s http://localhost:8000/response \
  -H "Content-Type: application/json" \
  -d '{"body":{"choices":[{"message":{"role":"assistant","content":"hello"}}]}}'
```

## Development

```bash
pip install -r requirements-dev.txt
pytest
```
