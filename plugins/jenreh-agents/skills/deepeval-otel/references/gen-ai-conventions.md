# GenAI conventions and migration

Use supported standard OpenTelemetry attributes when exporting to Azure or AWS.
The hyperscaler exporters do not implement the Confident AI attribute contract.
Existing `confident.*` values can survive as custom attributes but do not configure
cloud dashboards, online evaluation collections, or automatic schema conversion.

## Adapt existing instrumentation deliberately

| Existing field | Portable representation to consider |
| --- | --- |
| `confident.span.name` / `confident.trace.name` | Native span name on the relevant operation |
| `confident.span.type=agent` | Agent span with `gen_ai.operation.name=invoke_agent` |
| `confident.agent.name` | `gen_ai.agent.name` |
| `confident.llm.model` | Actual request/response model under the supported `gen_ai.*.model` key |
| `confident.span.provider` | Actual model provider under `gen_ai.provider.name` |
| `confident.llm.input_token_count` / `output_token_count` | Observed `gen_ai.usage.input_tokens` / `output_tokens` |
| `confident.tool.name` | `gen_ai.tool.name` on the actual tool operation |
| `confident.trace.environment` | Resource `deployment.environment.name`, adapted if the distribution needs a legacy key |
| Inputs, outputs, retrieval text, metadata | Review individually; omit content by default and select a supported schema when needed |
| Metric collection, expected tools, costs per token | Evaluation/product-specific; no assumed Azure/AWS equivalent |

This is implementation guidance, not an automatic converter. Trace-level values
must be placed on an appropriate resource or span, without copying sensitive
content. Avoid keeping duplicate instrumentation that creates two spans for the
same operation.

## Version compatibility

Inspect the SDK/framework and its emitted convention before editing attributes.
GenAI conventions have moved to a dedicated OpenTelemetry repository and remain
version-sensitive. Older integrations can emit `gen_ai.system`; newer ones use
`gen_ai.provider.name`. Preserve an existing supported schema, or migrate it as
an explicit change and verify the backend view. Export success does not establish
that every GenAI field is indexed or rendered by Foundry or AWS tooling.

## Official references

Checked 2026-10-20.

- [OpenTelemetry GenAI conventions entry point](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [GenAI attribute registry and migration notices](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)
- [Foundry client-side tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-client-side)
