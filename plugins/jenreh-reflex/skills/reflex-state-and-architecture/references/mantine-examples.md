# appkit_mantine example index

Real-world usage examples for `mn.*` components, by file. Use it to find a working
example before writing a component that `examples/components_example.py` does not
cover. For props and quirks, use the `appkit-mantine-reference` skill.

Additional real-world usage examples are available in the appkit repository:
**https://github.com/jenreh/appkit/tree/main/app/pages/examples**

| File | Components covered |
|---|---|
| `button_examples.py` | `mn.button`, `mn.action_icon`, `mn.action_icon.group` |
| `input_examples.py` | `mn.text_input`, `mn.textarea`, `mn.number_input`, `mn.tags_input`, `mn.password_input`, `mn.json_input`, `mn.slider`, `mn.range_slider`, `mn.switch` |
| `date_examples.py` | `mn.date_input`, `mn.date_picker_input`, `mn.date_time_picker`, `mn.month_picker_input`, `mn.time_input`, `mn.calendar` |
| `modal_examples.py` | `mn.modal`, `mn.modal.root`, `mn.modal.stack` |
| `overlay_examples.py` | `mn.tooltip`, `mn.hover_card` |
| `table_examples.py` | `mn.table`, `mn.table.thead/tbody/tr/th/td`, `sticky_header`, `with_table_border` |
| `charts_examples.py` | `mn.bar_chart`, `mn.line_chart`, `mn.area_chart` |
| `data_display_examples.py` | `mn.badge`, `mn.avatar`, `mn.card`, `mn.progress` |
| `navigation_examples.py` | `mn.tabs`, `mn.nav_link`, `mn.breadcrumbs` |
| `feedback_examples.py` | `mn.alert`, `mn.notification`, `mn.loader` |
| `combobox_examples.py` | `mn.select`, `mn.multi_select`, `mn.combobox` |

Always check the docs for:
- Correct prop names (e.g. `left_section` not `leftSection`, `with_border` not `withBorder`)
- Event handler signatures (`on_change`, `on_blur`, `on_visibility_change`)
- Controlled (`value=` + `on_change=`) vs uncontrolled (`default_value=` + `on_blur=`) usage
