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

  /* Ordered Lists Numbers & Hierarchy */
  .vditor-reset ol {
    list-style-type: decimal !important;
    list-style-position: outside !important;
    padding-left: 1.75rem !important;
  }
  .vditor-reset ol ol {
    list-style-type: lower-alpha !important;
  }
  .vditor-reset ol ol ol {
    list-style-type: lower-roman !important;
  }
  .vditor-reset ul {
    list-style-position: outside !important;
    padding-left: 1.75rem !important;
  }

  /* Dark Mode Table Styling */
  .vditor-reset table {
    border-collapse: collapse !important;
    width: 100% !important;
    margin-bottom: 1.5rem !important;
    border-spacing: 0 !important;
    border: 1px solid #374151 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
  }
  .vditor-reset table th,
  .vditor-reset table td {
    border: 1px solid #374151 !important;
    padding: 8px 14px !important;
    color: #e5e7eb !important;
    text-align: left !important;
  }
  .vditor-reset table th {
    background-color: #1f2937 !important;
    font-weight: 600 !important;
    color: #f9fafb !important;
    border-bottom: 2px solid #4b5563 !important;
  }
  .vditor-reset table tr {
    background-color: #111827 !important;
    border-top: 1px solid #374151 !important;
    transition: background-color 0.15s ease !important;
  }
  .vditor-reset table tbody tr:nth-child(2n) {
    background-color: #1a2234 !important;
  }
  .vditor-reset table tbody tr:hover {
    background-color: #243049 !important;
  }

  /* Ensure all toolbar tooltips float downwards below the toolbar */
  .vditor-toolbar .vditor-tooltipped::after {
    top: 100% !important;
    bottom: auto !important;
    margin-top: 6px !important;
    margin-bottom: 0 !important;
    transform: translateX(50%) !important;
    z-index: 1000 !important;
  }
  .vditor-toolbar .vditor-tooltipped::before {
    top: auto !important;
    bottom: -6px !important;
    border-bottom-color: #24292e !important;
    border-top-color: transparent !important;
    z-index: 1001 !important;
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
      'line', 'quote', 'list', 'ordered-list', 'check', 'outdent', 'indent', '|',
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
      },
      success(editorElement, msg) {
        try {
          const res = JSON.parse(msg);
          const filename = res.filename || 'image';
          const imgPath = res.relative_path || res.url || '';
          if (imgPath) {
            vditor.insertMD(`\n![${filename}](${imgPath})\n`);
            container.dispatchEvent(new CustomEvent('editor-typing', { bubbles: true }));
            container.dispatchEvent(new CustomEvent('editor-autosave', {
              detail: { content: vditor.getValue() },
              bubbles: true
            }));
          }
        } catch (e) {
          console.error('Error inserting uploaded image:', e);
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
      // Re-orient toolbar tooltips downwards to prevent clipping against container boundaries
      container.querySelectorAll('.vditor-toolbar [class*="vditor-tooltipped__"]').forEach(el => {
        el.className = el.className.replace(/vditor-tooltipped__[a-z]+/g, 'vditor-tooltipped__s');
      });

      // Escape & outdent listener for nested lists in IR mode
      const irElement = container.querySelector('.vditor-ir pre.vditor-reset');
      if (irElement) {
        function handleListEscape(e) {
          const selection = window.getSelection();
          if (!selection || !selection.rangeCount) return false;
          const range = selection.getRangeAt(0);
          const startNode = range.startContainer;

          const li = startNode.nodeType === 1 ? startNode.closest('li') : startNode.parentElement ? startNode.parentElement.closest('li') : null;
          if (!li) return false;

          const p = startNode.nodeType === 1 ? startNode.closest('p') : startNode.parentElement ? startNode.parentElement.closest('p') : null;
          const isPInsideLi = p && li && li.contains(p);
          const topList = li.closest('ul, ol');
          const parentLi = li.parentElement ? li.parentElement.closest('li') : null;

          // 1. Paragraph inside a list item (e.g. "parrafo")
          if (isPInsideLi) {
            const isAtStart = range.collapsed && range.startOffset === 0 && (startNode === p || startNode === p.firstChild || !startNode.previousSibling);
            const isPEmpty = p.textContent.replace(/[\u200B-\u200D\uFEFF]/g, '').trim() === '';

            // Trigger on Shift+Tab, or Enter on empty paragraph, or Backspace at start of paragraph
            if ((e.key === 'Tab' && e.shiftKey) || (e.key === 'Enter' && isPEmpty) || (e.key === 'Backspace' && isAtStart)) {
              e.preventDefault();
              e.stopPropagation();

              if (topList && topList.parentElement) {
                topList.parentElement.insertBefore(p, topList.nextSibling);
                p.setAttribute('data-block', '0');
                if (isPEmpty) {
                  p.innerHTML = '<wbr>';
                }

                const newRange = document.createRange();
                if (p.firstChild) {
                  newRange.setStart(p.firstChild, Math.min(range.startOffset, p.firstChild.textContent ? p.firstChild.textContent.length : 0));
                } else {
                  newRange.selectNodeContents(p);
                }
                newRange.collapse(true);
                selection.removeAllRanges();
                selection.addRange(newRange);

                container.dispatchEvent(new CustomEvent('editor-typing', { bubbles: true }));
                return true;
              }
            }
          }

          // 2. Empty nested list item (outdent to parent list level)
          const liText = li.textContent.replace(/[\u200B-\u200D\uFEFF]/g, '').trim();
          const isLiEmpty = liText === '';

          if (parentLi && (e.key === 'Enter' || (e.key === 'Tab' && e.shiftKey) || e.key === 'Backspace')) {
            if (isLiEmpty) {
              e.preventDefault();
              e.stopPropagation();

              const sublist = li.parentElement;
              parentLi.parentElement.insertBefore(li, parentLi.nextSibling);

              if (sublist && sublist.querySelectorAll('li').length === 0) {
                sublist.remove();
              }

              li.innerHTML = '<wbr>';
              const newRange = document.createRange();
              newRange.selectNodeContents(li);
              newRange.collapse(true);
              selection.removeAllRanges();
              selection.addRange(newRange);

              container.dispatchEvent(new CustomEvent('editor-typing', { bubbles: true }));
              return true;
            }
          }

          return false;
        }

        irElement.addEventListener('keydown', handleListEscape, true);

        // Also wire up toolbar outdent button click
        const outdentBtn = container.querySelector('.vditor-toolbar button[data-type="outdent"]') ||
                           container.querySelector('.vditor-toolbar [data-type="outdent"]');
        if (outdentBtn) {
          outdentBtn.addEventListener('click', function(e) {
            const fakeEvent = { key: 'Tab', shiftKey: true, preventDefault() {}, stopPropagation() {} };
            if (handleListEscape(fakeEvent)) {
              e.preventDefault();
              e.stopPropagation();
            }
          }, true);
        }
      }

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
        args = event.args if hasattr(event, "args") else event
        content = ""
        if isinstance(args, dict):
            detail = args.get("detail")
            if isinstance(detail, dict) and "content" in detail:
                content = str(detail.get("content", ""))
            elif "content" in args:
                content = str(args.get("content", ""))
        elif isinstance(args, str):
            content = args

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
