# Traced Evals

Tracing is the default single-turn eval path when the app can produce traces
through a DeepEval integration or manual instrumentation. The trace is the
end-to-end execution and spans are the components; component-level metrics are
attached to specific spans inside the same single-turn tracing eval, not split
into a separate test shape.

This reference covers the **eval-coupled** side of tracing: attaching metrics
to spans and the pytest/script shapes for traced evals. To **instrument** the
app — add `@observe`, wire framework integrations, set span types, tags, and
metadata — use the `deepeval-tracing` skill.

## Azure/AWS tracing compatibility

Cloud OTel spans do not automatically become native DeepEval spans for the
assertions below. When Azure/AWS is selected, keep operational tracing on that
provider and use the tracing skill's verified offline native instrumentation for
local evals. Do not add a Confident exporter or request login to get span metrics.
If no compatible local trace path is available, use the output-based evaluation
template explicitly and report that component metrics are unavailable. Hosted
reporting instructions apply only when that separate service is requested.

## Component / Span Metrics

When metrics belong to a specific component, keep them in the single-turn
tracing eval and attach them to the exact span they evaluate.

If a supported integration creates the span, stage metrics for the next span of
that type:

```python
from deepeval.tracing import next_retriever_span

from metrics import RETRIEVER_SPAN_METRICS


with next_retriever_span(metrics=RETRIEVER_SPAN_METRICS):
    run_ai_app_with_integration_tracing(golden.input)
```

If manual instrumentation or the integration supports observed component spans,
attach metrics directly to `@observe`:

```python
from deepeval.tracing import observe

from metrics import GENERATOR_LLM_SPAN_METRICS


@observe(type="llm", metrics=GENERATOR_LLM_SPAN_METRICS)
def call_model(messages): ...
```

Name span metric lists after the component, such as
`RETRIEVER_SPAN_METRICS`, `GENERATOR_LLM_SPAN_METRICS`, or
`ORDER_LOOKUP_TOOL_SPAN_METRICS`. Do not create one global component metric
list for the app. Use `next_agent_span`, `next_llm_span`, `next_tool_span`, or
`next_retriever_span` to match the span type the integration creates.

## Pytest vs Script Shapes

For CI/CD, prefer the pytest shape shown in each integration doc — pass the
`Golden` directly through the traced app and assert:

```python
@pytest.mark.parametrize("golden", dataset.goldens)
def test_agent(golden: Golden):
    run_ai_app_with_integration_tracing(golden.input)
    assert_test(golden=golden, metrics=TRACE_METRICS)
```

For scripts or iteration loops, use `evals_iterator` and pass the `Golden`
through the traced app:

```python
for golden in dataset.evals_iterator(metrics=TRACE_METRICS):
    run_ai_app_with_integration_tracing(golden.input)
```

Preserve native traced single-turn assertions when a verified offline integration
exists. When the application has only cloud OTel spans and no compatible native
DeepEval path, use the output-based template and document the unavailable local
component metrics.

## Confident AI

If the user chooses Confident AI results, confirm either `deepeval login` has
been run or `CONFIDENT_API_KEY` is exported. Prefer `CONFIDENT_API_KEY` for CI
and other non-interactive runs. After evals, use `deepeval view` to open the
latest hosted report when appropriate.
