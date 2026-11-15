# Local DeepEval evaluations alongside cloud tracing

The production path uses OTel instrumentation and the selected Azure/AWS exporter.
DeepEval is optional. Local evaluations may still need native DeepEval spans for
`assert_test(golden=...)`, `evals_iterator`, and component/span metrics. Do not
replace those native spans with cloud spans and assume the assertions still work.

## Local setup

1. Use local datasets/goldens and the project's configured evaluation model. Azure
   OpenAI and Amazon Bedrock are available model-provider choices where supported;
   they are independent of the telemetry backend.
2. Prefer a dedicated evaluation process/environment with no Confident account
   credentials or persisted login. Inspect auto-loaded configuration and dotenv
   sources before importing DeepEval; a missing shell variable alone is not proof
   of no saved credentials. Never print keys or alter a user's global login merely
   to run a test. Stop and explain unresolved automatic upload configuration.
3. Use only the native instrumentation required for local evaluation. Inspect its
   installed implementation for Confident exporters, background uploads, and SDK
   telemetry before enabling it; bypass hosted monitoring and prompt-management
   setup in the bundled examples. Do not add a Confident processor to the cloud
   provider just to obtain component metrics.
4. `CONFIDENT_TRACE_FLUSH=0` and verbosity switches are not network/upload controls.
   SDK usage-telemetry opt-outs are a separate concern from application-trace
   uploads. Verify the actual destinations instead of relying on those switches.
5. If an integration couples local evaluation to a hosted exporter and has no
   verified offline path, use isolated manual DeepEval evaluation instrumentation
   or the explicit output-based evaluation path in `deepeval`. Cloud production
   tracing can stay enabled; document any loss of local component metrics.
6. Keep eval artifacts and results local. Do not request Confident login, API keys,
   hosted datasets, dashboards, prompt objects, or `deepeval view` for this workflow.

Use the `deepeval` skill to choose datasets, metrics, evaluation model, and tests.
The model can still require Azure/AWS credentials and incur model costs. Running
local metrics does not automatically configure cloud-side online evaluations.

## Native trace compatibility

DeepEval's native `@observe` creates native trace-manager data. Its SDK/framework
adapters can use different tracing mechanisms, including OTel. Current upstream
interfaces do not provide a universal native-to-Azure/AWS exporter switch. Do not
invent `TRACE_DESTINATION` support on `trace_manager` or convert its REST API URL
into an OTLP endpoint. If both local spans and OTel spans are needed, verify each
pipeline and correlation explicitly; trace IDs are not automatically identical.

Official references:
[DeepEval local agent evaluation](https://deepeval.com/docs/getting-started-agents),
[tracing interoperability FAQ](https://deepeval.com/docs/faq), and
[upstream integration modes](https://github.com/confident-ai/deepeval/blob/main/deepeval/integrations/README.md).
