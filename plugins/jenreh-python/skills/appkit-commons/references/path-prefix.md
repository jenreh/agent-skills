# Serving below a path prefix (shared origin)

Read this before writing links, asset URLs, redirects, browser storage keys, or OAuth
redirect URLs in an app that may run below a `frontend_path`.

Several apps can share one origin (e.g. `https://x/knai`, `https://x/alloq`).
One setting drives it: `reflex.frontend_path`. `rxconfig.py` passes it to
`rx.Config(frontend_path=...)`. Export and backend must use the same value.

```yaml
# config.local.yaml
reflex:
  frontend_path: /knai   # leave out for the site root
```

Derived from it automatically:

| What | Site root | Below `/knai` | Override |
| --- | --- | --- | --- |
| Session cookie | `reflex_session` | `knai_session` | `authentication.session_cookie_name` |
| Local storage prefix | `""` | `knai_` | `authentication.storage_key_prefix` |
| `AuthenticationConfiguration.public_base_url` | `https://x` | `https://x/knai` | `server_url` already ending in `/knai` |
| OAuth `redirect_url` | `<public_base_url>/oauth/<provider>/callback` | same, carries `/knai` | `oauth_providers[].redirect_url` |

Helpers in `appkit_commons.public_path` (no Reflex import needed by callers):

```python
from appkit_commons.public_path import (
    public_path,  # "/img/logo.svg" -> "/knai/img/logo.svg"; URLs unchanged
    public_url,  # public_url(base, "/api/x") -> "<base>/knai/api/x"
    strip_public_prefix,  # "/knai/login" -> "/login" (router.url.path carries it)
    public_prefix,  # "/knai" or ""
    app_slug,  # "knai" or ""
)
from appkit_user.authentication.states import app_storage_key  # "knai_<name>"

rx.image(src=public_path("/img/logo.svg"))
download_url = public_path(f"/api/bpmn/diagrams/{diagram_id}/xml")
if strip_public_prefix(self.router.url.path) == "/login":
    ...
token: str = rx.LocalStorage(name=app_storage_key("my-key"), sync=True)

rx.link("Login", href="/login")  # app relative: React Router adds the basename
return rx.redirect("/login")  # same
```

Rules:

- Page routes in `rx.link(href=...)`, `rx.redirect(...)` and `@rx.page(route=...)`
  stay app relative. React Router adds the prefix; `public_path()` there doubles it.
- Everything the browser or server resolves without React Router gets the prefix:
  asset `src`, raw HTML `href`, HTTP redirects in ASGI middleware, REST/API URLs,
  URLs handed to JS or external services. Use `public_path()` (path) or
  `public_url()` (absolute URL).
- Route checks on `router.url.path` go through `strip_public_prefix()`.
- Every `rx.LocalStorage` / `rx.SessionStorage` name, every key written from
  `rx.call_script` JS and every `persist_key` uses `app_storage_key()`. Writer
  and reader must share one constant.
- Do not set OAuth `redirect_url` in YAML unless you must; an explicit value is
  used verbatim and skips the prefix. The provider's registered callback URL
  must include the prefix (GitHub accepts a subpath of the registered URL, so
  registering the origin root covers every prefix).
- Cookie and storage names are fixed at import time and baked into the export.
  Re-export after changing `frontend_path`. Test them in a fresh interpreter
  (`subprocess`), not in-process.
- In-process tests: `appkit_commons.testing.set_public_path_prefix(monkeypatch, "/knai")`.
- Not prefixable (owned by Reflex / React Router): sessionStorage `token`,
  localStorage `theme`, `last_compiled_theme`, `react-router-scroll-positions`.
  Apps sharing one Redis also need distinct `app_name`s or Redis DBs.
