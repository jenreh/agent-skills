# Resources, trace identity, and correlation

A trace groups spans through trace IDs, span IDs, parent context, and propagation.
There is no universal separate "trace attributes" object. Put service identity
on the provider's resource and operation facts on the relevant spans.

## Resource identity

Set `service.name` (`OTEL_SERVICE_NAME`) and, where known, `service.version` and
`deployment.environment.name` through `OTEL_RESOURCE_ATTRIBUTES`. Add real
hosting resource attributes from the deployment or a supported resource detector.
The telemetry destination is not necessarily the cloud hosting the application.
Do not label an on-premises application as Azure-hosted just because it exports
to Application Insights.

The Python template requires `OTEL_SERVICE_NAME` and calls `Resource.create`,
which includes standard environment resource attributes. Set the service name
explicitly rather than accepting an unknown service in the cloud UI. Some cloud
distributions consume older names such as `deployment.environment`; use their
version-specific requirements deliberately, without changing unrelated resources.

## Context and lifecycle

- Keep a root span for the actual request or job and child spans for its operations.
- Propagate W3C trace context across HTTP/messaging where supported; configure
  the AWS X-Ray header where the participating AWS integration needs it.
- Use the framework's async context propagation; do not create one trace per
  model/tool span or replace trace IDs when changing exporters.
- Keep session/conversation identifiers only when needed and approved. Avoid raw
  customer identifiers, credentials, and payloads in attributes or baggage.
- Choose sampling explicitly for the workload. For a smoke check, ensure the
  example is sampled; a sampled-out span cannot prove ingestion.
- Batch during normal operation; flush/shut down the provider at the owning
  application's lifecycle boundary, not after each request. A helper attaching an
  exporter must not shut down a provider owned by another subsystem.

## Evidence

Record the emitted trace ID, target resource/account/region, and check time.
Separate local creation, an export attempt, collector acceptance, and cloud
readback. Verify the same trace and child spans at the destination. For Foundry,
verify the application/agent relationship in its UI as well as stored spans.

## References

- [OpenTelemetry resource environment variables](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)
- [Deployment resource conventions](https://opentelemetry.io/docs/specs/semconv/resource/deployment-environment/)
- [Python context and instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
