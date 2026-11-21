---
name: deepeval-tracing
description: >
  Instrument AI agents, LLM applications, RAG pipelines, and chatbots with
  OpenTelemetry and send their traces to Azure Monitor Application Insights,
  Azure AI Foundry / Microsoft Foundry, or AWS X-Ray. Use when adding agent,
  model, retriever, and tool spans; integrating Pydantic AI, Strands, AgentCore,
  LangChain, LangGraph, or another framework; replacing Confident AI tracing;
  choosing native framework instrumentation or manual spans; or combining cloud
  observability with local DeepEval evaluations. Use deepeval-otel for cloud
  exporter, collector, identity, and endpoint setup, and deepeval for evaluation
  datasets, metrics, and test execution. No Confident AI account or login is needed.
license: Apache-2.0
compatibility: Requires the application's framework and an OpenTelemetry SDK plus the selected Azure/AWS exporter setup. DeepEval is optional and used only for local evaluation instrumentation.
metadata:
  short-description: Instrument AI applications and route traces to Azure Monitor, Azure AI Foundry, or AWS X-Ray.
  author: Arvato Systems AILA Solutions
  original-author: Confident AI
  category: observability
  tags: "tracing, instrumentation, opentelemetry, azure-monitor, ai-foundry, aws-xray, local-evaluation"
  jenreh.registry/id: "jenreh:jenreh-agents"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.1.0"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "Apache-2.0"
  jenreh.registry/source-path: "plugins/jenreh-agents/skills/deepeval-tracing"
  jenreh.registry/source-digest: "ecbfee83ca7c9ad85cefde68650bd331dac0e9ce72e8f6a9a6b04f9841bc13f6"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
  jenreh.registry/supported-channels: "beta,stable"
---

# AI tracing with Azure or AWS

Instrument the real application so agent, model, retrieval, and tool operations
are visible in the selected cloud. Use standard OpenTelemetry spans and supported
framework instrumentation. Keep `deepeval-tracing` as the skill name for existing
invocations; the cloud tracing path has no DeepEval or Confident AI dependency.

## Select the cloud destination

Reuse an existing explicit choice. If none exists, ask which destination to use:

| `TRACE_DESTINATION` | Backend | Required setup |
| --- | --- | --- |
| `azure-monitor` | Azure Monitor / Application Insights | Target Application Insights resource and connection string / ingestion identity |
| `azure-ai-foundry` | Application Insights linked to a Foundry project | Foundry project endpoint, Azure identity, linked resource, and supported AI instrumentation |
| `aws-xray` | AWS X-Ray via an ADOT/OpenTelemetry collector | Reachable collector, AWS account/region, and collector IAM identity |

Use the sibling [deepeval-otel skill](../deepeval-otel/SKILL.md) for the exporter,
authentication, collector, and region configuration. It owns the shared
[Python exporter template](../deepeval-otel/templates/cloud_otel_setup.py).
An Azure model endpoint, Bedrock model region, and telemetry destination are
independent choices. If the request only says "Azure", clarify general Monitor
versus Foundry. Missing configuration stops the dependent setup; do not choose
another service or region as a fallback.

## Workflow

1. Inspect the framework, SDK versions, deployment runtime, existing provider,
   processors, automatic instrumentation, and application entry points. Establish
   whether local DeepEval component evaluation is also required.
2. Configure or reuse one OpenTelemetry provider for the selected destination
   using `deepeval-otel`. For existing providers, attach its `create_exporter()`
   deliberately rather than calling another global initialization routine.
3. Read [cloud-instrumentation.md](references/cloud-instrumentation.md), the
   [integration index](references/integrations.md), and the matching bundled
   integration's cloud guidance. Prefer framework-native OTel support. Use a
   verified OTel instrumentor when appropriate, then manual spans for uncovered
   application boundaries. Verify APIs against installed versions and official docs.
4. Remove or replace the old production Confident export path: native DeepEval
   callbacks/wrappers that install it, Confident span processors/exporters, hosted
   prompt hooks, and destination-specific headers. Do not request `deepeval login`,
   a `CONFIDENT_API_KEY`, hosted datasets, or a Confident workspace. Inspect
   inherited configuration without printing secrets or modifying a user's global
   client profile. Do not treat a changed OTLP URL as conversion of native
   DeepEval `@observe` spans into OTel spans.
5. Instrument actual agent/model/retrieval/tool calls with meaningful names and
   observed attributes. Use [tracing.md](references/tracing.md) and the
   [manual span template](templates/cloud_spans.py). Preserve HTTP, database, and
   messaging parents where they explain the request. Avoid duplicate spans from
   framework instrumentation plus wrappers around the same operation.
6. Exclude prompt, response, document, embedding-vector, tool argument/result, and
   personal-identifier content by default. Apply framework controls before creating
   clients, inspect custom metadata and exceptions, and verify emitted spans.
   Record only real model identifiers, token counts, and operation outcomes.
7. When evaluations are requested, follow
   [local-evaluations.md](references/local-evaluations.md) and `deepeval`. Native
   DeepEval spans may support local component metrics; cloud OTel spans alone do
   not satisfy DeepEval's traced `Golden` assertions. Keep the evaluation process
   and cloud export lifecycle explicit. Do not install a Confident exporter to
   obtain local metrics.
8. Verify a representative request locally and read back its trace in the selected
   cloud. Check nesting, sampling, errors, and absence of payload content. In
   Foundry, verify an actual supported agent/model operation in the project's UI;
   generic span ingestion alone does not prove agent correlation.
9. Report changed instrumentation, destination, required configuration names,
   dependencies, local checks, and cloud evidence. Distinguish local span creation,
   exporter success, and cloud readback. State any unverified framework or backend.

## Bundled integration documents

The `integrations/` tree contains imported DeepEval evaluation references. Each
page begins with cloud guidance and links to the current workflow. The remaining
upstream examples are local evaluation references. Follow this skill's cloud
instructions when those examples mention Confident-hosted monitoring, prompt
management, credentials, or report publication; skip those hosted-service sections.
Their native SDK decorators and callbacks are not generic Azure/AWS exporters.

## Example requests and missing inputs

- "Trace this Pydantic AI agent in Azure Monitor using our existing provider."
- "Add Foundry client tracing with content capture disabled."
- "Trace this Strands app in AWS X-Ray through our ADOT collector."
- "Keep DeepEval component evals local and send operational telemetry to Azure."

If a framework has no verified OTel adapter, instrument its real invocation with
manual spans and report the reduced visibility. If a Foundry link, AWS collector,
identity, or framework package is missing, request that prerequisite by name.
Do not claim full component tracing or cloud delivery from a wrapper alone.

Adapted by Arvato Systems AILA Solutions from Confident AI's Apache-2.0 skill:
cloud destinations, instrumentation selection, content controls, and local
evaluation guidance replace the hosted-service workflow. Preserve its license.
