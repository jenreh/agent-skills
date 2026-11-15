# Framework instrumentation for cloud export

Use the version installed by the target project. Configure the selected Azure/AWS
provider through the sibling `deepeval-otel` skill once, then attach instrumentation
without installing an additional hosted-service exporter. Sources checked 2026-10-20.

## Pydantic AI

Use its native OTel instrumentation with the selected provider and content disabled:

```python
from pydantic_ai import Agent
from pydantic_ai.models.instrumented import InstrumentationSettings

# provider is the application's already-configured Azure/AWS SDK provider.
settings = InstrumentationSettings(tracer_provider=provider, include_content=False)
Agent.instrument_all(settings)
# Construct and run the application's agents after configuring instrumentation.
```

This applies to all agents deliberately; for an existing app preferring per-agent
configuration use its installed version's instrument/settings or Instrumentation
capability API. Logfire configuration and DeepEval's
`DeepEvalInstrumentationSettings` are not needed for cloud export. Model credentials
remain those of the application. Inspect metadata and custom spans independently.

Source: [Pydantic AI native OpenTelemetry and content controls](https://ai.pydantic.dev/logfire/).

## Strands

Configure the shared global OTel provider before creating Strands agents. Strands
can reuse that provider directly; do not call `setup_otlp_exporter()` again when
the chosen cloud exporter is already attached. Inspect the installed framework's
payload controls and emitted spans before running production traffic. Preserve
existing application model/tool configuration. DeepEval's `instrument_strands()`
is an evaluation adapter and is not required for this cloud path.

Sources: [Strands tracing](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/)
and [provider configuration API](https://strandsagents.com/docs/api/python/strands.telemetry.config/).

## AgentCore

For a hosted AgentCore runtime using AWS observability, reuse its ADOT/provider
setup and verify IAM, sampling, trace propagation, and the runtime's CloudWatch
observability configuration. Do not initialize another global provider or assume
the local collector template is deployed in the managed runtime. The DeepEval
`instrument_agentcore()` adapter is not the switch for AWS observability.

For locally running agents, use the selected cloud provider/collector path and the
underlying framework's OTel instrumentation. An Azure destination from an AWS-hosted
runtime needs an explicitly supported export configuration and network path; do not
claim the managed runtime's server-side telemetry moves with client spans.

Source: [AWS AgentCore observability configuration](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html).

## LangChain, LangGraph, and provider SDKs

Use a compatible framework-native or community OTel instrumentor with the existing
provider. OpenInference instrumentors can use a plain OTel provider without an
Arize/Phoenix account. Pin compatible dependencies and inspect the actual installed
instrumentor signature. For a supported instrumentor, the configuration pattern is:

```python
from openinference.instrumentation import TraceConfig

config = TraceConfig(hide_inputs=True, hide_outputs=True)
# instrumentor is an installed, version-verified OTel instrumentor instance.
instrumentor.instrument(tracer_provider=provider, config=config)
```

Review retrieval-document, embedding, tool-definition, and custom metadata capture
separately using the installed version's settings. LangChain-level instrumentation
covers callbacks propagated through LangChain; direct provider calls can require
the corresponding SDK instrumentor. Avoid overlapping model spans. A DeepEval
`CallbackHandler` creates evaluation-native data; it is not an Azure/AWS export
adapter. Keep native DeepEval callbacks only in the local evaluation process.

Sources: [OpenInference configuration](https://github.com/Arize-ai/openinference/blob/main/spec/configuration.md)
and [instrumentation packages](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation).

## Other frameworks, TypeScript, and vector stores

For OpenAI Agents, LlamaIndex, CrewAI, Google ADK, Hugging Face, Vercel AI SDK,
Mastra, and vector-store clients, prefer an OTel extension documented for the
installed version. Verify that it uses the selected provider and controls content
capture. The bundled DeepEval adapters are local evaluation references, not proof
that a particular cloud-native OTel adapter exists.

When no suitable extension is available, use the
[manual span template](../templates/cloud_spans.py) around real framework calls
and each app-owned model/tool/retrieval boundary. Report the granularity achieved.
For vector stores, preserve the application's client/connection settings and
instrument search/retrieval without emitting vectors, SQL parameters, queries,
retrieved documents, credentials, or database connection strings. General DB spans
may coexist with AI retrieval spans when they represent distinct operations.

In TypeScript use the framework's supported OTel hooks and the selected Azure/AWS
exporter; do not copy a Python package API or a `deepeval/tracing` decorator into a
JavaScript provider setup. Cloud export and local DeepEval evaluation remain
independent until a tested integration demonstrates otherwise.
