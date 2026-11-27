---
name: deepeval-otel
description: >
  Configure OpenTelemetry trace export to a selectable hyperscaler destination:
  Azure Monitor Application Insights for general applications, Azure AI Foundry
  (Microsoft Foundry) through the project's connected Application Insights, or
  AWS X-Ray through an ADOT/OpenTelemetry Collector. Use when instrumenting an
  application, AI agent, RAG pipeline, or chatbot; choosing Azure general vs
  Foundry tracing; migrating Confident AI OTLP export to Azure or AWS; configuring
  cloud exporters, authentication, regions, and trace correlation; or diagnosing
  missing cloud traces. Use the deepeval skill for evaluation datasets, metrics,
  and pytest evaluation suites.
license: Apache-2.0
compatibility: Requires the selected cloud resource, its access configuration, and an OpenTelemetry SDK. Python templates require only the selected destination's packages; see references/endpoint-and-exporter.md.
metadata:
  short-description: Export traces to Azure Monitor, Azure AI Foundry, or AWS X-Ray with a selectable destination.
  author: Arvato Systems AILA Solutions
  original-author: Confident AI
  category: observability
  tags: "opentelemetry, otlp, azure-monitor, application-insights, azure-ai-foundry, aws, xray"
  jenreh.registry/id: "jenreh:jenreh-agents"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.1.1"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "61ee12c96014fdfc2b7b4ba6f06c4da72c698255"
  jenreh.registry/source-license: "Apache-2.0"
  jenreh.registry/source-path: "plugins/jenreh-agents/skills/deepeval-otel"
  jenreh.registry/source-digest: "d0b87d54ea80e14cccdaca4c9f3cf11440df14b50bb06e28eac0371ad92a3d21"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
---

# OpenTelemetry export to Azure or AWS

Instrument the target application and route its traces to one explicit cloud
destination. Keep the skill name `deepeval-otel` for existing invocations.
DeepEval and a Confident AI account are not required for this workflow.

## Select the destination first

Reuse an explicit choice from the request or project configuration. Otherwise
ask which of the following three destinations to use before configuring export:

| Selection (`TRACE_DESTINATION`) | Destination | Required input |
| --- | --- | --- |
| `azure-monitor` | Azure Monitor / Application Insights for general application traces, including AI workloads | `APPLICATIONINSIGHTS_CONNECTION_STRING` and the intended Azure resource |
| `azure-ai-foundry` | Application Insights connected to an Azure AI Foundry / Microsoft Foundry project, with Foundry tracing instrumentation | `FOUNDRY_PROJECT_ENDPOINT`, Azure identity, and the project's Application Insights connection |
| `aws-xray` | AWS X-Ray through an ADOT or compatible OpenTelemetry Collector | Collector OTLP/HTTP traces URL, AWS account/region, and collector IAM identity |

The application can run outside the destination cloud. Azure and Foundry are
separate user choices even though both store telemetry in Application Insights.
A plain OTLP exporter cannot send to an Application Insights connection string.
For AWS, distinguish a collector URL from the AWS managed ingestion endpoint.

`TRACE_DESTINATION` is this template's selector, not a standard OTel variable.
Missing or unsupported values must stop setup; never pick a cloud, region,
resource, or fallback service silently. Missing inputs should be requested by
name; credentials stay in the environment or the project's secret store.

## Workflow

1. Inspect the language, dependency lockfile, deployment platform, existing
   OpenTelemetry provider, auto-instrumentation, collectors, and resource settings.
   Identify whether the task concerns general tracing, AI spans, or both.
2. Confirm the selected destination and resource/account/region. Read
   [endpoint-and-exporter.md](references/endpoint-and-exporter.md), then only the
   relevant [Azure Monitor](references/azure-monitor.md),
   [Foundry](references/azure-ai-foundry.md), or [AWS](references/aws-xray.md) guide.
3. Establish required packages and credentials using the target project's tools.
   Check APIs against the installed SDK version and the linked official docs.
   If a dependency, resource, identity, or network path is missing, explain the
   missing prerequisite and stop the dependent step. Do not fabricate access or
   create cloud resources merely to complete an example.
4. Reuse the existing provider and lifecycle. Add or replace the selected export
   processor deliberately; inspect and remove obsolete Confident AI processors,
   headers, and endpoints when migrating. Avoid duplicate instrumentation and
   unintended export to multiple destinations. Keep HTTP/database parent spans
   when they explain the application request; an AI-only filter is optional and
   must preserve trace structure.
5. For Python, adapt [cloud_otel_setup.py](templates/cloud_otel_setup.py).
   `create_exporter()` can attach to an existing provider. `configure_tracing()`
   is for a process without an existing SDK provider. For other languages, use
   the corresponding supported cloud exporter and preserve the same target choice.
   The AWS [collector template](templates/aws-collector.yaml) exports traces only.
6. Set service identity and parent/child context using
   [trace-attributes.md](references/trace-attributes.md). For AI operations use
   [span-attributes.md](references/span-attributes.md) and
   [gen-ai-conventions.md](references/gen-ai-conventions.md). Record only observed
   operations and token counts. Prompts, completions, retrieved text, tool payloads,
   and personal identifiers are excluded by default; inspect instrumentation
   defaults as well as custom spans before enabling content recording.
7. Verify in layers: configuration and syntax, local span creation, exporter or
   collector diagnostics, then ingestion in the selected cloud using a trace ID.
   Run one authorized representative application operation and confirm parent/child
   spans and errors. Foundry additionally needs a real instrumented agent/model
   operation; a generic smoke span does not prove its agent view is populated.
8. Report the selected target, changed files and dependencies, required environment
   variable names, evidence of ingestion, and any unverified step. Batch flush or a
   successful HTTP request alone is not proof of a usable trace in the destination.

## Example requests

- "Use deepeval-otel to export this API's traces to Azure Monitor, general mode."
- "Use deepeval-otel with Azure AI Foundry and the project's linked Application Insights."
- "Send this agent's traces to AWS X-Ray through our existing ADOT collector."

If asked only to "enable Azure tracing", offer `azure-monitor` and
`azure-ai-foundry` before choosing. If the Foundry Application Insights link or
AWS collector is absent, provide the required setup and continue only once it
exists. Do not reroute telemetry to another target to hide the missing input.

## Templates and provenance

The Python smoke example produces synthetic application spans only; replace it
with real operations when integrating. It does not call a model or create cloud
resources. Run it only against the intended target with authorized credentials.

This skill was adapted from Confident AI's Apache-2.0 OpenTelemetry skill.
The hyperscaler destinations, standard attributes, references, and templates were
changed by Arvato Systems AILA Solutions. Preserve the accompanying license.
