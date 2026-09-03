#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="${HOME}/.local/bin/knowledge-master"
ICON_DIR="${HOME}/.local/share/icons/hicolor/128x128/apps"
APPS_DIR="${HOME}/.local/share/applications"
DESKTOP_FILE="${APPS_DIR}/knowledge-master.desktop"

echo "=================================================="
echo "  Installing / Updating Knowledge Master Globally"
echo "=================================================="

# 1. Ensure UV is available
if ! command -v uv &> /dev/null; then
    echo "[Error] 'uv' command not found. Please install uv first."
    exit 1
fi

# 2. Build and install tool globally
echo "-> Installing CLI executable via uv tool..."
cd "${SCRIPT_DIR}"

PYTHON_BIN="/usr/bin/python3"
if [ ! -f "${PYTHON_BIN}" ]; then
    PYTHON_BIN="$(which python3)"
fi

uv tool install --python "${PYTHON_BIN}" --force --reinstall .

TOOL_CFG="${HOME}/.local/share/uv/tools/knowledge-master/pyvenv.cfg"
if [ -f "${TOOL_CFG}" ]; then
    sed -i 's/include-system-site-packages = false/include-system-site-packages = true/' "${TOOL_CFG}"
fi

# Ensure local development venv also has access to system WebKitGTK
if [ -f "${SCRIPT_DIR}/.venv/pyvenv.cfg" ]; then
    sed -i 's/include-system-site-packages = false/include-system-site-packages = true/' "${SCRIPT_DIR}/.venv/pyvenv.cfg"
fi

if [ ! -f "${BIN_PATH}" ]; then
    echo "[Error] Binary was not found at ${BIN_PATH}."
    exit 1
fi

echo "-> Executable verified at: ${BIN_PATH}"

# 3. Install Icon
echo "-> Installing application icon..."
mkdir -p "${ICON_DIR}"
cp -f "${SCRIPT_DIR}/assets/icon.png" "${ICON_DIR}/knowledge-master.png"

# 4. Generate Desktop Entry
echo "-> Generating desktop entry..."
mkdir -p "${APPS_DIR}"
cat <<EOF > "${DESKTOP_FILE}"
[Desktop Entry]
Version=1.0
Type=Application
Name=Knowledge Master
GenericName=Ebook Editor
Comment=Local Markdown Ebook Studio and Workspace Manager
Exec=${BIN_PATH} %U
Icon=knowledge-master
Terminal=false
Categories=Office;WordProcessor;Development;Publishing;
StartupWMClass=Knowledge Master
MimeType=text/markdown;text/plain;
Keywords=markdown;ebook;editor;writing;obsidian;
EOF

chmod 644 "${DESKTOP_FILE}"

# 5. Update desktop database if available
if command -v update-desktop-database &> /dev/null; then
    echo "-> Refreshing desktop application database..."
    update-desktop-database "${APPS_DIR}" 2>/dev/null || true
fi

echo ""
echo "=================================================="
echo "  Installation Successful!"
echo "=================================================="
echo "• Command:  knowledge-master"
echo "• Desktop:  Available in your applications menu"
echo "• Library:  ~/knowledge-master/ebooks/"
echo ""
