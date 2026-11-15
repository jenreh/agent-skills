"""Export smoke spans to one explicitly selected Azure or AWS destination.

See ../references/endpoint-and-exporter.md for packages and configuration.
TRACE_DESTINATION: azure-monitor | azure-ai-foundry | aws-xray.
This example creates no cloud resources and makes no model requests.
Adapt create_exporter() for applications with an existing provider.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SpanExporter
    from opentelemetry.trace import Tracer

DESTINATIONS = {"azure-monitor", "azure-ai-foundry", "aws-xray"}


def required(name: str) -> str:
    """Fail with the missing variable name, without printing its value."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} is required; see the selected destination guide")
    return value


def collector_endpoint() -> str:
    """Require a full collector OTLP/HTTP traces URL, not unsigned AWS ingestion."""
    endpoint = required("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    parsed = urlparse(endpoint)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.path != "/v1/traces"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT must be a collector HTTP(S) URL "
            "ending in /v1/traces, without embedded credentials, query, or fragment"
        )
    if parsed.hostname.startswith("xray.") and (
        parsed.hostname.endswith(".amazonaws.com")
        or parsed.hostname.endswith(".amazonaws.com.cn")
    ):
        raise ValueError(
            "Managed AWS ingestion requires a SigV4-capable ADOT setup; "
            "this template expects a collector endpoint"
        )
    return endpoint


def create_exporter() -> SpanExporter:
    """Create only the chosen exporter; no fallback or provider registration."""
    destination = required("TRACE_DESTINATION")
    if destination not in DESTINATIONS:
        raise ValueError(
            "TRACE_DESTINATION must be azure-monitor, azure-ai-foundry, or aws-xray"
        )
    if destination == "aws-xray":
        endpoint = collector_endpoint()
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        return OTLPSpanExporter(endpoint=endpoint)

    if destination == "azure-monitor":
        connection_string = required("APPLICATIONINSIGHTS_CONNECTION_STRING")
    else:
        endpoint = required("FOUNDRY_PROJECT_ENDPOINT")
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=endpoint, credential=credential) as project,
        ):
            connection_string = (
                project.telemetry.get_application_insights_connection_string()
            )
        if not connection_string:
            raise ValueError(
                "The Foundry project has no Application Insights connection"
            )

    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

    # If the resource requires Entra ingestion, adapt credential= here as documented.
    # Project discovery credentials alone do not configure ingestion authentication.
    return AzureMonitorTraceExporter(
        connection_string=connection_string, disable_offline_storage=True
    )


def configure_tracing() -> TracerProvider:
    """Initialize a clean process once; existing SDK providers own their lifecycle."""
    service_name = required("OTEL_SERVICE_NAME")
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    if not isinstance(trace.get_tracer_provider(), trace.ProxyTracerProvider):
        # Reinitializing a configured provider is a runtime state error.
        raise RuntimeError(  # noqa: TRY004
            "Tracing already has an SDK provider; attach create_exporter() to it "
            "instead of initializing another provider"
        )
    exporter = create_exporter()
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider


def run_example(tracer: Tracer) -> str:
    """Emit generic synthetic spans; actual AI usage must come from the real app."""
    with tracer.start_as_current_span("otel-export-smoke-test") as root:
        root.set_attribute("app.test_run", True)
        with tracer.start_as_current_span("smoke-test-child"):
            pass
        return format(root.get_span_context().trace_id, "032x")


if __name__ == "__main__":
    try:
        provider = configure_tracing()
    except ImportError as error:
        raise SystemExit(
            f"Missing destination dependency: {error.name}; "
            "see references/endpoint-and-exporter.md"
        ) from error
    try:
        trace_id = run_example(provider.get_tracer("cloud-otel-smoke-test"))
    finally:
        provider.shutdown()
    print(f"Export attempted for smoke trace {trace_id}; verify cloud ingestion.")
