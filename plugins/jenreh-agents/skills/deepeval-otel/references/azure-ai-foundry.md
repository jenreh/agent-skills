# Azure AI Foundry / Microsoft Foundry tracing

Select `azure-ai-foundry` for tracing associated with a Foundry project. Confirm
the project endpoint and connect Application Insights to that project first.
Foundry's trace storage uses that linked Application Insights resource; this
mode does not introduce a separate generic Foundry OTLP endpoint.

## Resolve the linked resource

Set `FOUNDRY_PROJECT_ENDPOINT` to the actual project endpoint. The Python template
uses `DefaultAzureCredential` and
`AIProjectClient.telemetry.get_application_insights_connection_string()` to
resolve the project's linked resource, then uses the Azure Monitor exporter.
It deliberately does not fall back to an unrelated
`APPLICATIONINSIGHTS_CONNECTION_STRING` when project discovery fails.

Use a supported `azure-ai-projects` version for the actual project's API generation.
The current client tracing guide uses the 2.x SDK; older hub/project APIs differ.
Use the deployment's identity locally or in Azure; `az login` is an option for
local development. The principal needs access to read the project connection.
Querying traces and ingesting them have separate access requirements.

## Instrument the application

After configuring the provider, enable the SDK's tracing before creating the
application's Foundry/OpenAI clients. For a compatible Python SDK:

```python
import os

os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"

from azure.ai.projects.telemetry import AIProjectInstrumentor

AIProjectInstrumentor().instrument()
```

Use the installed SDK's supported framework instrumentation for agent/model/tool
spans. The exporter template alone emits only generic smoke spans; it does not
instrument Foundry or call a model. Keep prompt/response and tool payload
capture off unless requested. Custom function decorators can capture content
independently of the environment flag, so inspect them too.

## Verify

Run one authorized real agent operation. Check its trace in linked Application
Insights, then check Foundry's Traces view and agent correlation. Resource linkage,
supported instrumentation, agent identifiers, and propagated context determine
what appears in the Foundry UI; any arbitrary span is not automatically an agent
trace. Keep existing server-side traces and correlate client spans rather than
recreating the same operation. Client-side GenAI instrumentation is currently
marked preview in the linked guide; record the versions actually used.

Missing endpoint, Azure identity, project permissions, or Application Insights
connection must produce an actionable prerequisite, not an alternate export target.

## Official references

Checked 2026-10-20; verify version-specific instrumentation before applying it.

- [Connect Application Insights and set up Foundry tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup)
- [Foundry client tracing and configuration](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-client-side)
- [Azure AI Projects SDK and telemetry APIs](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects)
