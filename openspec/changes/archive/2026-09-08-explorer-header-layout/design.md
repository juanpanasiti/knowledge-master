# Technical Design: Explorer Header Layout and Lifecycle Fixes

## Context

The file explorer in `FileTreeComponent` (`src/ebook_editor/ui/components/file_tree.py`) renders four collapsible accordion sections: `Content`, `Resources`, `Assets`, and `Dist`. NiceGUI's `ui.expansion` component wraps Quasar's `QExpansionItem`. 

Currently, all four sections place their title row directly inside the expansion context manager without specifying a slot. In Quasar, elements declared in the default slot are placed in the collapsible content body (`QExpansionItem__content`), leaving the native header completely blank except for the expand chevron icon. When an accordion section collapses, the body is unmounted or hidden, causing section titles, badges, and action buttons to vanish completely.

In addition, dialog callbacks for creating or renaming files call `self.render()` before calling `ui.notify()`. Because `self.render()` clears `self.container`, the active event slot's parent is removed from the DOM tree, causing `ui.notify()` to raise `RuntimeError: The parent element this slot belongs to has been deleted.`

## Goals / Non-Goals

**Goals:**
- Place section identity (icon, title, badge, action button) inside Quasar's `header` slot via `with exp.add_slot("header"):` across all four sections.
- Ensure the header remains permanently visible regardless of section expansion or collapse state.
- Isolate click events on action buttons (`+`, upload) so interacting with them does not toggle the parent expansion state.
- Fix dialog event ordering so `ui.notify()` executes before `self.container.clear()` destroys the DOM slot context.

**Non-Goals:**
- Modifying backend workspace models (`EbookWorkspace`), data schemas, or file system watchers.
- Redesigning file tree items, chapter drag/drop, or context menus.
- Altering other UI panels (`git_panel.py`, `metadata_panel.py`, `editor.py`).

## Decisions

### 1. Structure Headers with `with exp.add_slot("header"):`
Quasar's `QExpansionItem` provides a scoped `#header` slot that replaces the default label while retaining the expand chevron toggle at the right edge.
```python
with ui.expansion(...) as exp:
    with exp.add_slot("header"):
        with ui.row().classes("flex-1 items-center justify-between pr-2"):
            with ui.row().classes("items-center gap-1.5"):
                ui.icon(icon_name, size="1rem").classes(icon_color)
                ui.label(title).classes("text-xs font-semibold uppercase tracking-wider text-gray-300")
                ui.badge(str(count), color=badge_color).props("dense rounded text-color=...").classes("text-[10px] px-1.5 py-0")
            if action_button:
                action_button()
    
    with ui.column().classes("w-full p-1 gap-1 items-stretch"):
        # Collapsible file items
```
*Rationale*: Using `flex-1 items-center justify-between` inside the `header` slot ensures that the icon, title, and count badge stay left-aligned, any action button sits right before the chevron, and the chevron toggle remains anchored to the far right.
*Alternatives Considered*: Setting `ui.expansion(text=..., icon=...)`. Rejected because Quasar's standard text/icon props cannot host the count badge or custom action buttons.

### 2. Isolate Action Button Click Events
By default, clicking anywhere on a `QExpansionItem` header toggles the section open or closed. Action buttons inside the header (`+` in Content and Resources, `upload` in Assets) must open their dialogs without toggling the section state.
*Rationale*: Intercepting the DOM click event on the button with `js_handler='(e) => { e.stopPropagation(); emit(); }'` stops event bubbling to the parent `QItem` before Quasar can trigger `toggle()`.
*Alternatives Considered*: Setting `expand-icon-toggle=True` on `ui.expansion`. Rejected because users expect clicking anywhere on the header bar (outside of action buttons) to expand or collapse the section.

### 3. Reorder Notification Execution in Dialog Callbacks
In `_show_new_file_dialog` and `_show_rename_dialog`:
```python
# Before:
self.render()
self.on_select_chapter(new_f)
ui.notify(f"Created '{new_f.name}'", type="positive")  # CRASH: parent slot deleted

# After:
ui.notify(f"Created '{new_f.name}'", type="positive")
self.render()
self.on_select_chapter(new_f)
```
*Rationale*: Emitting `ui.notify()` before calling `self.render()` ensures the active client context is resolved before `self.container.clear()` disposes of the triggering button's parent element.

## Risks / Trade-offs

- **[Risk]** Header content overflow on narrow sidebars.
  - **Mitigation**: Use compact typography (`text-xs`, uppercase tracking-wider), minimal padding (`pr-2`), and dense badge dimensions (`text-[10px] px-1.5 py-0`) so all elements comfortably fit within typical sidebar widths (200px+).
- **[Risk]** Quasar chevron alignment conflicts with header slot content.
  - **Mitigation**: Use `flex-1` on the header row container so Quasar's default right-side chevron naturally sits after the action button without overlapping.
