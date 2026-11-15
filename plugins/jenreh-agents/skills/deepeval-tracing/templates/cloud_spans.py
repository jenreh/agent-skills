"""Manual AI operation spans using the application's Azure/AWS OTel provider.

Adapted by Arvato Systems AILA Solutions for cloud-native instrumentation.
Configure the provider with deepeval-otel before invoking application operations.
No DeepEval, account login, payload capture, or exporter initialization is used.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.trace import Span, SpanKind, Status, StatusCode


@contextmanager
def operation_span(
    operation: str, target: str, *, kind: SpanKind = SpanKind.INTERNAL
) -> Iterator[Span]:
    """Trace one actual operation, excluding arguments, results, and error text.

    Works around synchronous calls and across an await inside the with block.
    Reuse framework-native spans when they already cover the same operation.
    """
    if not operation.strip() or not target.strip():
        raise ValueError("An actual operation and target name are required")
    tracer = trace.get_tracer("cloud-ai-operations")
    with tracer.start_as_current_span(
        f"{operation} {target}",
        kind=kind,
        attributes={"gen_ai.operation.name": operation},
        record_exception=False,
        set_status_on_exception=False,
    ) as span:
        try:
            yield span
        except Exception as error:
            span.set_attribute("error.type", type(error).__name__)
            span.set_status(Status(StatusCode.ERROR))
            raise
