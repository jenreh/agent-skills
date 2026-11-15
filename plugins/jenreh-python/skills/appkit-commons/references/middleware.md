# ASGI middleware

Read this when wiring `api_transformer` middleware (HTTPS behind a proxy, security
headers).

`appkit_commons.middleware` holds two pure ASGI middlewares for Reflex's
`api_transformer`. Do not copy them into an app.

```python
from appkit_commons.middleware import ForceHTTPSMiddleware, SecurityHeadersMiddleware


def add_security_headers(asgi_app: ASGIApp) -> ASGIApp:
    return SecurityHeadersMiddleware(asgi_app)


def add_https_middleware(asgi_app: ASGIApp) -> ASGIApp:
    return ForceHTTPSMiddleware(asgi_app, trusted_hosts=config.app.trusted_proxies)


rx.App(api_transformer=[create_rest_api(), add_security_headers, add_https_middleware])
```

- `ForceHTTPSMiddleware` sets `scope["scheme"]` from `X-Forwarded-Proto`; it never
  redirects. Pass `trusted_hosts` (the proxy addresses) wherever the backend port
  can be reached without the proxy.
- `SecurityHeadersMiddleware` adds `X-Content-Type-Options`, `Referrer-Policy`,
  `Content-Security-Policy: frame-ancestors 'self'` and, on https, HSTS. Headers a
  route sets itself are kept. A full CSP stays with the proxy (Reflex needs inline
  scripts).
- Reflex applies transformers in list order, each wrapping the previous. Put
  `SecurityHeadersMiddleware` before `ForceHTTPSMiddleware`, so it sits inside it and
  sees the corrected scheme when it decides on HSTS.
- Tests: `BASE_SECURITY_HEADERS` and `HSTS` are module constants; assert on them.
