# Destination and exporter selection

Choose exactly one target before editing telemetry configuration. These are the
Python template's explicit choices; they are not interchangeable URLs.

| Target | Export path | Configuration | Authentication |
| --- | --- | --- | --- |
| `azure-monitor` | OTel SDK -> Azure Monitor trace exporter -> Application Insights | `APPLICATIONINSIGHTS_CONNECTION_STRING` | Resource's supported ingestion configuration; Entra when required |
| `azure-ai-foundry` | OTel SDK + Foundry instrumentation -> Azure Monitor trace exporter -> project's linked Application Insights | `FOUNDRY_PROJECT_ENDPOINT`; SDK resolves linked connection string | Azure identity for project discovery; ingestion authentication separately |
| `aws-xray` | OTel SDK -> OTLP/HTTP collector -> `awsxray` exporter -> X-Ray | `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` on app; `AWS_REGION` on collector | Collector's AWS credential chain / IAM role |

## Install only the selected dependencies

Use the target project's package manager and lock compatible versions. These
package lists describe the Python examples, not dependencies of this marketplace.

| Target | Packages |
| --- | --- |
| All Python examples | `opentelemetry-api`, `opentelemetry-sdk` |
| Azure Monitor | `azure-monitor-opentelemetry-exporter` |
| Foundry | Azure Monitor packages plus `azure-ai-projects`, `azure-identity`, `azure-core-tracing-opentelemetry` |
| AWS collector route | `opentelemetry-exporter-otlp-proto-http`; collector distribution containing `awsxray` |

Do not mix the manual provider template with an auto-instrumentation distribution
that already owns the global provider. Attach `create_exporter()` to the existing
provider, or configure export through that distribution.

## Transport and migration rules

- An Application Insights connection string is Azure exporter configuration,
  not an OTLP URL. Do not append `/v1/traces` to it or send it as a bearer token.
- The AWS template uses an explicit OTLP/HTTP **traces URL**, including
  `/v1/traces`, for the collector. `OTEL_EXPORTER_OTLP_ENDPOINT` is the standard
  base URL variable; this template deliberately requires the signal-specific
  `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` to avoid ambiguous path handling.
- HTTP on localhost is suitable for a shared host/network namespace. Remote
  collectors need the deployment's TLS, authentication, and network controls.
  A container's localhost is not another container unless they share a namespace.
- Managed AWS X-Ray OTLP ingestion needs SigV4-capable export. It is an alternative
  ADOT setup, not a URL replacement in the template's plain OTLP exporter.
- Remove obsolete `CONFIDENT_API_KEY` references, `x-confident-api-key` headers,
  Confident AI exporters, and inherited `OTEL_EXPORTER_OTLP_HEADERS` or
  `OTEL_EXPORTER_OTLP_TRACES_HEADERS` that belong to the old route. Never forward
  an old destination's credentials to a new service.
- Change proprietary `confident.*` instrumentation only where needed, using
  the [migration guide](gen-ai-conventions.md). Custom attributes are not an
  automatic mapping into cloud-specific GenAI dashboards or online evaluations.

The language-neutral design is a tracer provider, resource identity, batch
processor, and destination-specific exporter. Follow the language's official
Azure or AWS integration for the concrete package names.
