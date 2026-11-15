# Azure Monitor: general application tracing

Use `TRACE_DESTINATION=azure-monitor` for API, worker, service, and AI application
traces stored in Azure Monitor Application Insights. A Foundry project is not
required. Identify the intended resource, region, and ingestion access settings.

## Configure

Set `APPLICATIONINSIGHTS_CONNECTION_STRING` from the target resource without
printing its value. Add `azure-monitor-opentelemetry-exporter` and the OTel SDK
to the target project's dependencies. The template constructs an
`AzureMonitorTraceExporter` and attaches it to a batch processor.
Microsoft's Azure Monitor distribution (`configure_azure_monitor`) is an
alternative when the project wants its managed auto-instrumentation and signals;
do not initialize both providers.

```sh
export TRACE_DESTINATION=azure-monitor
export OTEL_SERVICE_NAME=orders-api
# Supply APPLICATIONINSIGHTS_CONNECTION_STRING through the existing secret setup.
python cloud_otel_setup.py
```

Connection strings select an Application Insights resource; they do not grant
portal/query access. If ingestion requires Microsoft Entra ID, adapt the exporter
to use a supported `TokenCredential` and the ingestion role required by the
resource (for example Monitoring Metrics Publisher). Project discovery identity
and ingestion identity are separate concerns. Use managed/workload identity in
the hosting environment where available. Do not re-enable local authentication
to bypass an access failure.

The template disables Azure exporter offline storage for its smoke example.
Choose retry, sampling, storage, and retention settings for the actual workload.
It configures traces only; existing logs and metrics have their own lifecycle.

## Verify

Record the smoke trace ID and find its operation in Application Insights under
transaction diagnostics or query the resource's request/dependency tables
(`requests`/`dependencies` or workspace `AppRequests`/`AppDependencies`). Match
`operation_Id` / `OperationId` and inspect child spans. Check resource selection,
sampling, exporter diagnostics, networking, and ingestion delay when absent.
Use a real application request for the final integration check.

## Official references

Checked 2026-10-20; verify against the target project's installed packages.

- [Azure Monitor trace exporter and manual Python examples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/README.md)
- [Azure Monitor distribution configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-configuration)
- [Microsoft Entra authentication for Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/azure-ad-authentication)
