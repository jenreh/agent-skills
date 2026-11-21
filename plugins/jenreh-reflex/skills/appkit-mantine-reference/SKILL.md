---
name: appkit-mantine-reference
description: "MUST invoke when generating mn.* based UIs or the user asks how to use, configure, or debug any mn.* or appkit_mantine component. appkit_mantine is NOT in Claude's training data — always use this skill rather than guessing at APIs. Covers building forms, tables, drawers, modals, tooltips, color pickers, date/time pickers, charts, and navigation; looking up correct props; debugging on_change handler types (NumberInput sends float|str, DateInput sends str|\"\"); troubleshooting component quirks like tooltips on disabled elements, overlays not closing, or props having no effect. Targets Mantine 9.7.3 on Reflex 0.10."
metadata:
  author: jens-rehpoehler
  version: "1.9"
  license: MIT
  jenreh.registry/id: "jenreh:jenreh-reflex"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.4.1"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "MIT"
  jenreh.registry/source-path: "plugins/jenreh-reflex/skills/appkit-mantine-reference"
  jenreh.registry/source-digest: "805c8a72966e3428da7a0f31a41889eabeb2768e790e0e23032a1168defb8727"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
  jenreh.registry/supported-channels: "beta,stable"
---

# Using appkit_mantine Components

## Quick reference

**Import**: `import appkit_mantine as mn`
**All components use lowercase factory functions**: `mn.button()`, `mn.text_input()`, `mn.modal()`
**Versions**: Mantine **9.7.3** (`appkit_mantine.base.MANTINE_VERSION`) on Reflex **0.10**.
The references describe exactly this API; every prop they list exists.

## Inheritance hierarchy

```
MantineComponentBase          → library, CSS import, MantineProvider injection
  ↓
MantineLayoutComponentBase    → w, h, m*, p*, bg, c, display, pos, flex, etc.
  ↓
MantineInputComponentBase     → label, description, error, success, value, on_change, sections, etc.
  ↓
Specific components           → only component-unique props
```

- `MantineOverlayComponentBase` extends `MantineLayoutComponentBase` → Modal, Drawer shared props

## Creating components

Use factory functions, not class constructors:

```python
import appkit_mantine as mn

mn.text_input(label="Name", value=State.name, on_change=State.set_name)
mn.button("Submit", on_click=State.submit, variant="filled")
mn.stack(mn.text("Hello"), mn.text("World"), gap="md")
```

## Event handler patterns

Reflex 0.10 creates no automatic `set_*` setters, so every `State.set_x` used in
these docs is an explicit `@rx.event` method you write, typed to match the payload
below.

Default `on_change` uses `rx.event.input_event` (event.target.value). Some components override this:

| Component | on_change receives | Pattern |
|---|---|---|
| TextInput, PasswordInput, Textarea | event object | `on_change=State.set_value` (standard) |
| NumberInput | raw number or `""` | Handler must accept `float \| str` |
| Select, SegmentedControl | string value or `None` | Direct value, null→`""` |
| MultiSelect, TagsInput, CheckboxGroup | `list[str]` | Direct array |
| RadioGroup | `str` | Direct selected value |
| DateInput | string or `None` | Null converted to `""` |
| Checkbox, Switch | `bool` (checked) | `event.target.checked` extraction |
| Slider | `int \| float` | Direct value |
| RangeSlider | `list[int \| float]` | Direct list `[min, max]` |
| Tabs, Pagination | `str` or `int` | Direct value |
| Menu | `bool` (opened state) | via `on_change` |

### NumberInput handler example

```python
@rx.event
def set_price(self, val: float | str) -> None:
    if val == "":
        self.price = 0.0
        return
    with contextlib.suppress(ValueError):
        self.price = float(val)
```

### DateInput handler example

```python
@rx.event
def set_date(self, value: str) -> None:
    self.selected_date = value  # "" when cleared, ISO string otherwise
```

### JavaScript function props

Render props, predicates and formatters (`render_option`, `render_pill`,
`render_event`, `can_drop_event`, `value_formatter`, `render_notification`, ...)
run in the browser. Pass a JS function, never a Python lambda:

```python
mn.tree_select(
    data=State.tree, render_pill=rx.Var("({ node }) => node.label.toUpperCase()")
)
```

Dict props (`*_props`, `styles`, `class_names`, chart `series`) reach React
unchanged: Reflex camelCases keyword props, not dict keys, so write keys as
Mantine names them (`{"startTime": "08:00:00"}`, `styles={"content": {"minHeight": 300}}`).

## Component index

Find the component here, then read its reference file before writing code.
Sub-components are namespaced: `.group` means `mn.checkbox.group`, not `mn.checkbox_group`.

| Reference | Components (`mn.*`) | Pick notes |
|---|---|---|
| [inputs-text](references/inputs-text.md) | `text_input`, `number_input`, `password_input`, `textarea`, `masked_input`, `json_input`, `form.*` | Custom label/description/error layout: `form.wrapper`, `form.label`, `form.error`. Hidden field: `form.input(type="hidden", ...)` |
| [inputs-selection](references/inputs-selection.md) | `select`, `multi_select`, `autocomplete`, `native_select`, `tags_input`, `tree_select`, `cascader`, `rich_select`, `combobox_popover` | Hierarchy: `tree_select`; drill-down columns: `cascader`. Custom-rendered options: `rich_select.map(data, renderer=...)`. Dropdown on a plain button: `combobox_popover` |
| [inputs-toggle](references/inputs-toggle.md) | `checkbox` (`.group`, `.card`), `radio` (`.group`, `.card`), `switch`, `chip` (`.group`), `segmented_control`, `fieldset` | Related inputs under a legend: `fieldset` |
| [inputs-datetime](references/inputs-datetime.md) | `date_input`, `date_picker_input`, `date_time_picker`, `inline_date_time_picker`, `month_picker_input`, `year_picker_input`, `time_input`, `time_picker`, `time_grid`, `calendar`, `date_picker`, `month_picker`, `year_picker`, `mini_calendar` | |
| [inputs-specialized](references/inputs-specialized.md) | `slider`, `range_slider`, `file_input`, `pin_input`, `rating`, `color_input`, `color_picker`, `hue_slider`, `alpha_slider`, `angle_slider` | Button-style upload: `file_input`; drag-and-drop: `dropzone` (extensions) |
| [layout](references/layout.md) | `stack`, `group`, `flex`, `grid`, `simple_grid`, `container`, `center`, `box`, `space`, `divider`, `affix`, `focus_trap`, `app_shell` (`.resizable`), `aspect_ratio`, `collapse`, `transition`, `marquee`, `portal`, `scroller`, `visually_hidden`, `floating_window`, `overflow_list`, `splitter` (`.pane`) | Vertical: `stack`; horizontal: `group`. Header/navbar/footer/aside: `app_shell` |
| [overlays](references/overlays.md) | `modal`, `drawer`, `alert_dialog`, `dialog`, `popover`, `tour` (`.step`), `loading_overlay`, `overlay`, `floating_indicator` | Centered: `modal`; side panel: `drawer`; confirmation: `alert_dialog`; small floating panel: `dialog` |
| [data-display](references/data-display.md) | `button`, `action_icon`, `close_button`, `unstyled_button`, `card`, `paper`, `accordion`, `avatar`, `badge`, `image`, `background_image`, `indicator`, `timeline`, `number_formatter`, `rolling_number`, `spoiler`, `theme_icon`, `color_swatch`, `kbd`, `tooltip`, `hover_card`, `data_list`, `empty_state` | Label/value pairs: `data_list`; "no data" with a CTA: `empty_state` |
| [feedback](references/feedback.md) | `alert`, `notification`, `progress`, `ring_progress`, `semi_circle_progress`, `loader`, `skeleton` | Toasts from event handlers: `notifications.show` (extensions) |
| [navigation](references/navigation.md) | `tabs`, `breadcrumbs`, `pagination`, `stepper`, `nav_link`, `navigation_progress`, `anchor`, `burger`, `table_of_contents`, `scroll_area` (`.autosize`, `.autoscroll`, `.stateful`), `rich_text_editor`, `markdown_preview`, `toggle`, `toolbar` | Chat/streaming scroll: `scroll_area.autoscroll`. Rich text (Tiptap): `rich_text_editor` |
| [menu](references/menu.md) | `menu` (`.search`, `.checkbox_item`, `.radio_group`, `.context_menu`), `menubar` | Desktop-style File/Edit/View bar: `menubar` |
| [table](references/table.md) | `table` | |
| [tree](references/tree.md) | `tree` | |
| [typography](references/typography.md) | `text`, `title`, `code`, `list_`, `blockquote`, `highlight`, `mark`, `typography_styles_provider` | HTML/Markdown with Mantine styles: `typography_styles_provider` |
| [charts](references/charts.md) | `line_chart`, `bar_chart`, `area_chart`, `composite_chart`, `donut_chart`, `pie_chart`, `radar_chart`, `radial_bar_chart`, `scatter_chart`, `bubble_chart`, `funnel_chart`, `sankey_chart`, `sunburst_chart`, `bullet_chart`, `gauge_chart`, `waffle_chart`, `matrix_chart`, `candlestick_chart`, `sparkline`, `heatmap`, `treemap`, `bars_list`, `chart_brush` | KPI: `gauge_chart`, `bullet_chart`, `waffle_chart` |
| [schedule](references/schedule.md) | `schedule` (`.day_view`, `.week_view`, `.month_view`, `.year_view`, `.mobile_month_view`), `resources_schedule`, `resources_day_view`, `resources_week_view`, `resources_month_view`, `agenda_view` | Rooms/people as rows: `resources_*` |
| [extensions](references/extensions.md) | `carousel` (`.slide`), `dropzone`, `modals_provider`, `notifications_provider` + `notifications.show`, `lightbox`, `lightbox_api`, `action_bar`, `json_viewer` | Bulk actions on selected rows: `action_bar` |
| [maps](references/maps.md) | `map` (`.marker`, `.popup`, `.route`, `.arc`, `.geojson`, `.cluster`, `.navigation`, `.controls`, `.directions_panel`) | |
| [theme](references/theme.md) | `create_theme`, `mantine_provider`, `virtual_color`, `theme_wrapper`, `ThemeState`, `mermaid_zoom_script` | Scoped theme override: `mantine_provider`. Mermaid click-to-zoom: `mermaid_zoom_script` |
| [App helpers](#app-helpers) | `delete_dialog`, `LoadingState`, `with_loading_reset`, `sticky_header_style` | Row delete confirmation: `delete_dialog` |

## App helpers

Ready-made pieces for appkit apps, exported from `appkit_mantine`:

| Helper | Purpose |
| --- | --- |
| `mn.delete_dialog(title, content, on_click, icon_button=False, action_loading=False, **trigger_props)` | `mn.alert_dialog` with a trash trigger (`mn.button` or `mn.action_icon`) and a German confirmation text naming `content` |
| `mn.LoadingState` | `is_loading`, `is_loading_message`, `set_is_loading(bool)`; drives the wait cursor |
| `mn.with_loading_reset(on_load)` | Returns the page `on_load` list (handler, list or `None`) with `LoadingState.set_is_loading(False)` appended |
| `mn.ThemeState` | `gray_color`, `radius`, `scaling`, `appearance` for the Radix theme |
| `mn.theme_wrapper(content)` | `rx.theme` bound to `ThemeState`, wait cursor while `LoadingState.is_loading` |
| `mn.sticky_header_style` | Style dict for a sticky page header (z-index, shadow, clip path) |

```python
mn.delete_dialog(
    title="Benutzer löschen",
    content=user.name,
    on_click=UserState.delete_user(user.user_id),
    icon_button=True,
    variant="subtle",
    color="red",
)


@rx.page(route="/reports", on_load=mn.with_loading_reset(ReportState.on_load))
def reports_page() -> rx.Component:
    return mn.theme_wrapper(mn.app_shell(mn.app_shell.main(report_content())))
```

Pages behind a login use `authenticated_page` (appkit-user), which applies both
helpers itself.

## Reflex 0.10 notes

appkit requires `reflex>=0.10.1`. State vars are descriptors on the declaring
class, which matters for the state and tests behind `mn.*` UIs:

- No auto setters: write each `set_*` handler yourself (see above).
- Do not pass `State._backend_var` as a prop or child (it is a `Field` now);
  use `.default_value()` or a regular var.
- Do not assign `State.var = x` or `monkeypatch.setattr` state vars in tests;
  use `State.__fields__["x"].set_default(...)`.
- Background tasks must write inherited vars inside `async with self`.
- `backend_vars`, `inherited_vars`, `get_skip_vars()` are gone; use
  `get_fields()`.
- Wrapper authors: `get_event_triggers` is a `@classmethod`; keep new props
  snake_case (Reflex camelCases them) and regenerate stubs with `task pyi`.
- Handlers that return `mn.notifications.*` / `rx.call_script` specs work
  unchanged.

## Critical rules

1. **Use only props the references list.** Reflex 0.10 raises no error for an
   undeclared keyword: it silently turns it into CSS (`mn.text(foo="bar")` renders
   `css: {foo: "bar"}`), which is the usual cause of "this prop has
   no effect". For a Mantine prop the wrapper does not declare, pass it as
   `custom_attrs={"camelCaseName": value}`. Undeclared *event* props do fail loudly
   (`ValueError: ... does not take in an on_change event trigger`).
2. **Never redeclare inherited props** — base classes provide ~40 common props
3. **MantineProvider is auto-injected** — no manual wrapping needed
4. **Use `rx.cond` and `rx.foreach`** — never bare Python `if` or `for` in components
5. **Use `&` and `|`** in `rx.cond`, not `and`/`or`
6. **Controlled vs uncontrolled** — use `value` + `on_change` (controlled) or `default_value` (uncontrolled), not both
7. **Path prefix** — apps served below `frontend_path` (e.g. `/knai`): wrap absolute asset `src` (images, files; not page links) in `public_path("/img/x.png")` (`appkit_commons.public_path`) and every `persist_key` in `app_storage_key("x")` (`appkit_user.authentication.states`). Examples below use bare paths for brevity.

## Namespace components (compound pattern)

Sub-components hang off the parent (`mn.accordion.item`, `mn.popover.target`,
`mn.app_shell.header`), never `mn.parent_child`:

```python
mn.tabs(
    mn.tabs.list(
        mn.tabs.tab("Tab 1", value="1"),
        mn.tabs.tab("Tab 2", value="2"),
    ),
    mn.tabs.panel(rx.text("Content 1"), value="1"),
    mn.tabs.panel(rx.text("Content 2"), value="2"),
    value=State.active_tab,
    on_change=State.set_active_tab,
)
```

## Mantine style props

All layout/input components take Mantine's style props directly
(`mn.text_input(label="Email", w="100%", maw=400, mt="md", p="sm")`): `w`, `h`, `miw`, `maw`, `mih`, `mah`, `m`, `my`, `mx`, `mt`, `mb`, `ml`, `mr`, `p`, `py`, `px`, `pt`, `pb`, `pl`, `pr`, `bg`, `c`, `display`, `pos`, `flex`, `opacity`, `fz`, `fw`, `ta`, `td`, `bd`, `hidden_from`, `visible_from`, `light_hidden`, `dark_hidden`.

## Colors

Mantine colors are `<name>.<shade>` with shade **0–9** (0 lightest, 9 darkest); a bare
name uses the theme's `primary_shade` (6 by default):

```python
c="blue.6"  # text color
bg="gray.0"  # background color
bd="1px solid red.3"  # border
"color": "teal.5"  # in chart series dict
c=rx.cond(State.ok, "teal.6", "red.6")  # conditional color: just switch the strings
"var(--mantine-color-blue-4)"  # same color as a CSS value (style dicts, light-dark())
```

Common color names: `blue`, `gray`, `red`, `green`, `teal`, `orange`, `violet`, `yellow`, `pink`, `dark`.
Use `c="dimmed"` for secondary text. Do not mix in `rx.color("blue", 4)`: that is the
Radix 1–12 scale and does not follow the Mantine theme.

## Anti-Patterns

| Anti-pattern | Correct approach |
|---|---|
| `rx.vstack` / `rx.hstack` for layout | `mn.stack` / `mn.group` |
| `rx.box` as a container | `mn.card` or `mn.paper` |
| `rx.text` / `rx.heading` for typography | `mn.text` / `mn.title` |
| `mn.list(...)` | `mn.list_(...)` — underscore avoids shadowing Python `list` built-in |
| `mn.checkbox_group`, `mn.radio_group`, `mn.chip_group`, `mn.popover_target`, `mn.dropzone_idle`, `mn.app_shell_header`, `mn.carousel_slide` | Namespaces: `mn.checkbox.group`, `mn.popover.target`, `mn.app_shell.header`, ... |
| Inline styles as strings `style="..."` | Mantine style props: `c="blue.6"`, `fw="bold"`, `p="md"` |
| Custom background on `mn.card` via `background_color`/`--card-bg` | `mn.card` ignores these; wrap in `rx.box` with desired `style` |
| `rx.el.input(type="hidden", ...)` in a form | `mn.form.input(type="hidden", name=..., value=..., display="none")` |
| Hand-written delete confirmation `alert_dialog` per table | `mn.delete_dialog(...)` |
| `.to_string()` for user-facing numbers | `mn.number_formatter(value=..., thousand_separator=".", decimal_separator=",")` |

## ScrollArea variants

See [references/navigation.md](references/navigation.md) for full ScrollArea docs.

| Variant | When to use |
|---|---|
| `mn.scroll_area.autosize(...)` | **Preferred for lists** — grows to `mah`, then scrolls |
| `mn.scroll_area.autoscroll(...)` | Chat/streaming — auto-scrolls to bottom on new content |
| `mn.scroll_area(...)` | Fixed-height scroll container |
| `mn.scroll_area.stateful(...)` | Navbar with `persist_key=app_storage_key("navbar_scroll_area")` |

---

**→ For state management, event handlers, background tasks, form validation, page factory, service registry, repository pattern, database models, and project architecture, use the `reflex-state-and-architecture` skill.**
