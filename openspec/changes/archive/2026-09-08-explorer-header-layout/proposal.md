# Change Proposal: Explorer Header Layout and Lifecycle Fixes

## Why

In the sidebar file explorer, accordion sections (`Content`, `Resources`, `Assets`, `Dist`) currently place their title, section icon, item count badge, and action buttons inside the collapsible body rather than Quasar's dedicated `header` slot of `ui.expansion`. As a result, when an accordion section is collapsed, the header appears completely blank with only a bare chevron toggle, hiding section titles and counts. Furthermore, file creation dialog callbacks trigger `self.render()` before `ui.notify()`, leading to DOM slot parent deletion runtime errors when notifications attempt to resolve client context from destroyed parent slots.

Placing section titles, counters, and action triggers into the persistent expansion header restores expected explorer visibility and polish, while correcting dialog notification order eliminates runtime exceptions.

## User Impact

Users will see clean, informational accordion headers for all four explorer sections at all times, even when collapsed. Users can easily identify each section, inspect file counts at a glance, and trigger quick actions without having to expand sections first. In addition, creating chapters or resource files from dialogs will complete smoothly without slot deletion runtime errors.

## Goals

- Render section icons, titles (`Content`, `Resources`, `Assets`, `Dist`), item count badges, and action buttons (`+`, upload) inside the persistent expansion `header` slot.
- Ensure section identity, counts, and actions remain visible and accessible in both expanded and collapsed states.
- Prevent click event propagation on header action buttons so clicking `+` or upload opens the respective dialog without toggling the accordion open/closed state.
- Fix UI notification and dialog lifecycle in `file_tree.py` to ensure `ui.notify()` executes before clearing or destroying parent container slots during re-render.

## Non-Goals

- Changing the file categorization structure or adding new explorer sections beyond the existing four (`Content`, `Resources`, `Assets`, `Dist`).
- Redesigning the file list item styles, file sorting logic, or context menus.
- Modifying backend workspace models or file system storage.

## What Changes

- **Accordion Section Header Slot**: Refactor `_render_content_section`, `_render_resources_section`, `_render_assets_section`, and `_render_dist_section` in `FileTreeComponent` to attach the header row to `ui.expansion.add_slot('header')` instead of nesting it in the collapsible body.
- **Action Button Click Isolation**: Configure `@click` event handlers on header action buttons to stop DOM event propagation (`e.stopPropagation()`) so clicking actions does not toggle the parent expansion container.
- **Explorer Re-render & Notification Lifecycle**: Reorder `ui.notify()` and `self.render()` in file creation and rename handlers in `file_tree.py` so notifications are emitted before `self.container.clear()` destroys the active event context slot.

## Capabilities

### New Capabilities
*(None)*

### Modified Capabilities
- `ebook-workspace`: Update explorer accordion requirements to specify that section titles, icons, item count badges, and section action buttons are hosted in the persistent header slot of each collapsible section, remaining visible and functional when collapsed, with event isolation for action buttons.

## Impact

- **Affected Code**: `src/ebook_editor/ui/components/file_tree.py`.
- **APIs & Dependencies**: NiceGUI 2.x / Quasar `q-expansion-item` header slot. No new dependencies or external API alterations.
- **SemVer Impact**: `patch` (bug fix and UX polish on existing UI components; version bump from `0.4.0` to `0.4.1` in `pyproject.toml`).
