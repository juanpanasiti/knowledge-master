"""Vditor NiceGUI component for instant rendering markdown editing."""

import json
from typing import Callable
from nicegui import core, ui

# Ensure Vditor CSS and JS headers are added to the NiceGUI client head
VDITOR_HEAD_HTML = """
<link rel="stylesheet" href="/static/vendor/vditor/index.css" />
<script src="/static/vendor/vditor/index.min.js"></script>
<style>
  .vditor {
    border: none !important;
    height: 100% !important;
    min-height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    background-color: transparent !important;
  }
  .vditor-toolbar {
    background-color: transparent !important;
    border-bottom: 1px solid rgba(128, 128, 128, 0.2) !important;
    padding: 0 12px !important;
    flex-shrink: 0 !important;
    width: 100% !important;
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    clear: both !important;
  }
  .vditor-toolbar__item {
    float: none !important;
  }
  .vditor-content {
    flex: 1 1 0% !important;
    width: 100% !important;
    height: 100% !important;
    min-height: 0 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    position: relative !important;
    clear: both !important;
  }
  .vditor-ir {
    background-color: transparent !important;
    flex: 1 1 0% !important;
    width: 100% !important;
    height: 100% !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 0 !important;
  }
  .vditor-ir pre.vditor-reset {
    box-sizing: border-box !important;
    transition: max-width 0.2s ease, margin 0.2s ease, border-radius 0.2s ease, box-shadow 0.2s ease !important;
  }

  /* Centered Reading Mode (Paper Sheet) */
  .editor-sheet-centered {
    background-color: #030712 !important;
  }
  .editor-sheet-centered .vditor-toolbar {
    background-color: #030712 !important;
  }
  .editor-sheet-centered .vditor-ir {
    background-color: #030712 !important;
    align-items: center !important;
  }
  .editor-sheet-centered pre.vditor-reset,
  .editor-sheet-centered pre.vditor-reset:focus {
    width: 100% !important;
    max-width: 56rem !important;
    min-height: calc(100% - 4rem) !important;
    margin: 1.5rem auto 3rem auto !important;
    padding: 2.5rem 3.5rem 6rem 3.5rem !important;
    background-color: #1e2430 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.45) !important;
  }

  /* Full Width Mode (Expansive Canvas) */
  .editor-sheet-full {
    background-color: #1e2430 !important;
  }
  .editor-sheet-full .vditor-toolbar {
    background-color: #1e2430 !important;
  }
  .editor-sheet-full .vditor-ir {
    background-color: #1e2430 !important;
    padding: 0 !important;
  }
  .editor-sheet-full pre.vditor-reset,
  .editor-sheet-full pre.vditor-reset:focus {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 100% !important;
    margin: 0 !important;
    padding: 2rem 3rem 6rem 3rem !important;
    background-color: #1e2430 !important;
    color: #e5e7eb !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
  }
</style>
<script>
window.kmVditorInstances = window.kmVditorInstances || {};

window.initKmEditor = function(containerId, initialValue, theme, retries = 0) {
  const container = document.getElementById(containerId);
  if (!container || typeof Vditor === 'undefined') {
    if (retries < 50) {
      setTimeout(() => window.initKmEditor(containerId, initialValue, theme, retries + 1), 50);
    }
    return;
  }

  if (window.kmVditorInstances[containerId]) {
    try {
      window.kmVditorInstances[containerId].destroy();
    } catch (e) {
      console.warn('Destroying previous vditor failed:', e);
    }
  }

  let debounceTimer = null;
  const vditor = new Vditor(containerId, {
    value: initialValue || '',
    mode: 'ir',
    lang: 'en_US',
    theme: theme === 'dark' ? 'dark' : 'classic',
    preview: {
      theme: theme === 'dark' ? 'dark' : 'light',
      markdown: {
        toc: true,
        mark: true,
        footnotes: true,
        autoSpace: true
      }
    },
    cdn: '/static/vendor/vditor',
    cache: { enable: false },
    height: '100%',
    toolbarConfig: { pin: true },
    toolbar: [
      'headings', 'bold', 'italic', 'strike', '|',
      'line', 'quote', 'list', 'ordered-list', 'check', '|',
      'code', 'inline-code', 'insert-before', 'insert-after', '|',
      'upload', 'link', 'table', '|',
      'undo', 'redo', '|',
      'fullscreen'
    ],
    upload: {
      url: '/api/workspace/upload-asset',
      linkToImgUrl: '/api/workspace/upload-asset',
      accept: 'image/*',
      fieldName: 'file',
      format(files, responseText) {
        try {
          const res = JSON.parse(responseText);
          return JSON.stringify({
            msg: res.msg || '',
            code: res.code || 0,
            data: {
              errFiles: [],
              succMap: { [res.filename]: res.url }
            }
          });
        } catch (e) {
          return responseText;
        }
      }
    },
    input(val) {
      clearTimeout(debounceTimer);
      container.dispatchEvent(new CustomEvent('editor-typing', { bubbles: true }));
      debounceTimer = setTimeout(() => {
        container.dispatchEvent(new CustomEvent('editor-autosave', {
          detail: { content: val },
          bubbles: true
        }));
      }, 500);
    },
    after() {
      container.dispatchEvent(new CustomEvent('editor-ready', { bubbles: true }));
    }
  });

  window.kmVditorInstances[containerId] = vditor;
};

window.setKmEditorValue = function(containerId, value) {
  const instance = window.kmVditorInstances[containerId];
  if (instance) {
    instance.setValue(value || '');
  }
};

window.getKmEditorValue = function(containerId) {
  const instance = window.kmVditorInstances[containerId];
  return instance ? instance.getValue() : '';
};

window.setKmEditorTheme = function(containerId, theme) {
  const instance = window.kmVditorInstances[containerId];
  if (instance) {
    const vditorTheme = theme === 'dark' ? 'dark' : 'classic';
    const contentTheme = theme === 'dark' ? 'dark' : 'light';
    instance.setTheme(vditorTheme, contentTheme);
  }
};
</script>
"""


class VditorEditor:
    """NiceGUI wrapper for the Vditor instant rendering markdown editor."""

    _head_injected = False

    def __init__(
        self,
        initial_value: str = "",
        theme: str = "dark",
        width_mode: str = "centered",
        on_save: Callable[[str], None] | None = None,
        on_typing: Callable[[], None] | None = None,
    ) -> None:
        self.initial_value = initial_value
        self.theme = theme
        self.width_mode = width_mode
        self.on_save = on_save
        self.on_typing = on_typing
        self.container_id = f"vditor-{id(self)}"
        self._current_content = initial_value
        self.is_ready = False

        if not VditorEditor._head_injected:
            ui.add_head_html(VDITOR_HEAD_HTML)
            VditorEditor._head_injected = True

        sheet_class = "editor-sheet-centered" if width_mode == "centered" else "editor-sheet-full"
        with ui.column().classes(f"w-full h-full flex-1 min-h-0 overflow-hidden items-stretch {sheet_class}") as self.wrapper:
            self.element = ui.element("div").props(f'id="{self.container_id}"').classes("w-full h-full flex-1 min-h-0 overflow-hidden")

        # Listen for events dispatched from client-side JS
        self.element.on("editor-ready", self._handle_ready)
        self.element.on("editor-typing", self._handle_typing)
        self.element.on("editor-autosave", self._handle_autosave)

        # Automatically schedule editor initialization once container mounts
        ui.timer(0.05, self.init_editor, once=True)

    def _run_js(self, script: str) -> None:
        """Safely execute JavaScript via element's client instance."""
        try:
            if core.loop and core.loop.is_running():
                if hasattr(self.element, "client") and self.element.client:
                    self.element.client.run_javascript(script)
                else:
                    ui.run_javascript(script)
        except Exception:
            pass

    def init_editor(self) -> None:
        """Trigger client-side Vditor initialization."""
        value_escaped = json.dumps(self._current_content)
        theme_escaped = json.dumps(self.theme)
        self._run_js(
            f"window.initKmEditor('{self.container_id}', {value_escaped}, {theme_escaped});"
        )

    def set_width_mode(self, width_mode: str) -> None:
        """Switch between 'centered' and 'full' writing sheet width."""
        self.width_mode = width_mode
        sheet_class = "editor-sheet-centered" if width_mode == "centered" else "editor-sheet-full"
        self.wrapper.classes(remove="editor-sheet-centered editor-sheet-full", add=sheet_class)

    def _handle_ready(self, _) -> None:
        self.is_ready = True

    def _handle_typing(self, _) -> None:
        if self.on_typing:
            self.on_typing()

    def _handle_autosave(self, event) -> None:
        content = event.args.get("content", "")
        self._current_content = content
        if self.on_save:
            self.on_save(content)

    def set_content(self, content: str) -> None:
        """Set editor content dynamically from Python."""
        self._current_content = content
        value_escaped = json.dumps(content)
        self._run_js(
            f"window.setKmEditorValue('{self.container_id}', {value_escaped});"
        )

    def set_theme(self, theme: str) -> None:
        """Update editor theme ('dark' or 'light')."""
        self.theme = theme
        theme_escaped = json.dumps(theme)
        self._run_js(
            f"window.setKmEditorTheme('{self.container_id}', {theme_escaped});"
        )

    @property
    def content(self) -> str:
        """Return the most recently saved content."""
        return self._current_content
