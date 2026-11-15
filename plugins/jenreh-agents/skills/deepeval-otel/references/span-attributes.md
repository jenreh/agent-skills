# Span attributes and application instrumentation

Create spans around actual operations and preserve their natural parent/child
relationships. Keep HTTP, database, and messaging instrumentation for general
applications. For AI applications add agent, model, retrieval, and tool spans
where the framework does not already supply them.

## AI operations

Prefer supported OpenTelemetry GenAI conventions emitted by the installed
instrumentation. The convention evolves; do not assume every backend recognizes
every attribute or rename existing instrumentation blindly.

| Operation | Useful attributes when observed |
| --- | --- |
| Agent invocation | `gen_ai.operation.name=invoke_agent`, `gen_ai.agent.name`, `gen_ai.agent.id` |
| Model request | `gen_ai.operation.name=chat` (or the actual supported operation), `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model` |
| Token usage | `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` as integers from the real response |
| Tool execution | `gen_ai.operation.name=execute_tool`, `gen_ai.tool.name` |

The model provider is independent of the telemetry destination. For example,
exporting to Azure Monitor does not make an Amazon Bedrock model an Azure model.
Do not invent model identifiers, response content, costs, tool calls, or token
counts to populate a dashboard. Use the framework's convention version and
backend guidance for span kinds and supported GenAI views.

## Errors and values

Record real exceptions with the native OTel exception event and error status.
Review exception messages for secrets before forwarding them. Attributes use
primitive values or homogeneous primitive arrays. For ordinary custom metadata,
flatten to namespaced primitive attributes; JSON-encode only a bounded value
when the chosen backend/schema requires a string. Payload events and structured
GenAI messages need the installed instrumentation's supported schema.

Prompts, completions, documents, and tool arguments/results are excluded by
default. A flag disabling automatic content recording does not sanitize custom
spans or exception messages. Use allowlisted diagnostic fields and actual timings.

## References

- [OpenTelemetry GenAI conventions and current location](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenTelemetry Python instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
- [Migration and version guidance](gen-ai-conventions.md)
