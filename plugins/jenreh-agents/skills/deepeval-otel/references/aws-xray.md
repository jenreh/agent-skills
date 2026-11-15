# AWS X-Ray through OpenTelemetry

Use `TRACE_DESTINATION=aws-xray`. Identify the AWS account, region, deployment
platform, and existing collector/ADOT installation before choosing the export path.

## Collector route used by the template

The application sends OTLP/HTTP to a reachable collector. The collector's
`awsxray` exporter converts spans into X-Ray segments and signs AWS API calls
using its credential chain. Start from [aws-collector.yaml](../templates/aws-collector.yaml),
using an ADOT or contrib distribution/version containing its configured components.
Set `AWS_REGION` in the collector environment and use the intended IAM role
(ECS task role, EKS workload identity, instance role, or a local development
profile). The basic write path needs `xray:PutTraceSegments`; sampling and other
features can require additional actions. Keep role permissions scoped to use.

```sh
export TRACE_DESTINATION=aws-xray
export OTEL_SERVICE_NAME=orders-agent
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://127.0.0.1:4318/v1/traces
python cloud_otel_setup.py
```

The collector template binds to loopback, suitable for a shared network namespace.
For a separate container, pod, or remote gateway, set a reachable receiver binding
and application URL deliberately; configure network access, TLS, and authentication
for that topology. Do not expose an unauthenticated receiver publicly.
The application does not need AWS credentials for this local collector route;
the collector does. Do not add AWS access keys or Confident AI headers to OTLP.

Preserve W3C `traceparent`/`tracestate` for services using W3C propagation. Where
AWS services use `X-Amzn-Trace-Id`, configure a compatible X-Ray propagator in the
instrumentation and validate correlation at the boundary. Do not replace a
working propagator merely because export uses X-Ray.

## Optional managed OTLP ingestion

AWS also supports direct regional OTLP trace ingestion using a supported ADOT
SDK with SigV4 authentication. This is a different startup/exporter setup from
the collector template. Follow the official ADOT instructions for the language,
version, protocol, credential chain, and region. A stock unsigned OTLP exporter
pointed at `https://xray.<region>.amazonaws.com/v1/traces` is insufficient.
When ADOT already owns the provider, configure it rather than calling the template's
provider setup. Do not combine both routes unless dual export was requested.

## Verify

Check collector export failures, AWS identity/region, and ingestion networking.
Find the recorded trace ID in the intended account's X-Ray trace view and inspect
its service/child spans. Trace export alone does not configure CloudWatch Logs,
metrics, Application Signals, or GenAI dashboards. Those features need their own
supported instrumentation/configuration. X-Ray annotations/indexing and span
conversion may differ from raw OTel; verify important attributes in the stored trace.

## Official references

Checked 2026-10-20.

- [AWS OpenTelemetry Python tracing and propagation](https://docs.aws.amazon.com/xray/latest/devguide/migrate-xray-to-opentelemetry-python.html)
- [OpenTelemetry Collector X-Ray exporter configuration](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/awsxrayexporter)
- [AWS direct OTLP ingestion with ADOT](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLP-UsingADOT.html)
- [X-Ray IAM policy examples](https://docs.aws.amazon.com/xray/latest/devguide/security_iam_id-based-policy-examples.html)
