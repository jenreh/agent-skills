# Manual and framework tracing for Azure/AWS

Configure the selected destination with `deepeval-otel` before creating application
clients. Use the global SDK provider or pass that same provider to framework
instrumentation. A tracer provider owns the processors and export lifecycle;
application helpers must not initialize or shut it down per request.

## Prefer supported framework spans

Follow [cloud-instrumentation.md](cloud-instrumentation.md). Framework spans can
capture model, tool, agent, and retrieval boundaries that an outer wrapper cannot
see. Add manual spans only for missing boundaries and application-owned orchestration.
Keep parent context across awaited tasks, HTTP calls, and messaging. Export to
Azure/AWS through the one selected pipeline.

## Manual application boundaries

Copy [cloud_spans.py](../templates/cloud_spans.py) into the target application's
telemetry module and adapt the import to that location:

```python
from cloud_spans import operation_span

# run_existing_agent and user_input belong to the real application.
with operation_span("invoke_agent", "support-agent"):
    result = run_existing_agent(user_input)
```

For asynchronous code, use the same context manager around the awaited operation:

```python
with operation_span("invoke_agent", "support-agent"):
    result = await run_existing_agent(user_input)
```

The template creates spans using the configured OTel provider, records operation
names, marks failures with exception types, and re-raises the original exception.
It does not store arguments, results, exception messages, or stack traces. Inspect
framework instrumentation separately; a safe wrapper cannot sanitize its children.

For a remote model request, use the real model identifier, `operation="chat"`, and
`kind=SpanKind.CLIENT`. For an app-owned tool use `execute_tool`; for retrieval use
the convention supported by the instrumentation, such as `retrieval`. Update
observed attributes on the returned span:

```python
from opentelemetry.trace import SpanKind

with operation_span("chat", actual_model_name, kind=SpanKind.CLIENT) as span:
    response = call_existing_model()
    span.set_attribute("gen_ai.request.model", actual_model_name)
    # Add usage integers only when the real response supplies them.
```

These are integration examples, not runnable model calls. Replace app-owned names
with the actual application functions; do not generate synthetic successful model
responses, tools, or token counts to demonstrate tracing.

## Attributes and privacy

Use service/resource identity from the exporter setup and supported `gen_ai.*`
attributes for AI operations. The model provider is independent of the telemetry
backend. Use native OTel status and context, and bounded primitive attributes.
Store useful non-content metadata such as application version or a retrieval index
name only where it is appropriate; avoid raw user/session identifiers.

Keep input/output capture disabled in framework instrumentation. Explicitly inspect
prompts, completions, retrieved chunks, tool schemas/payloads, SQL parameters,
HTTP headers, exception messages, logs, and custom spans before allowing content.
Do not equate replacing `update_current_span` calls with disabling the SDK's
automatic capture. Native DeepEval `@observe` is reserved for the optional local
evaluation path described in [local-evaluations.md](local-evaluations.md).

## Verification

Run one authorized actual request; confirm agent/model/tool nesting and an error
case locally. Match its trace ID in Application Insights, the Foundry project's
linked resource/UI, or the intended AWS account's X-Ray trace view. Ensure content
is excluded. A batch flush or successful HTTP response is not cloud readback.

Sources: [OTel Python instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
and [GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
