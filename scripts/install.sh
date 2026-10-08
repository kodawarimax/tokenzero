#!/usr/bin/env bash
set -e

# ==============================================================================
# TokenZero Engine Installer
# ==============================================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_BIN="${HOME}/.local/bin"
TARGET_LIB="${HOME}/.local/lib/tokenzero"
CLAUDE_SKILLS="${HOME}/.claude/skills"
CODEX_SKILLS="${HOME}/.agents/skills"
CODEX_SKILLS_V2="${HOME}/.codex/skills"
GEMINI_TEMPLATES="${HOME}/.gemini/antigravity/templates/skills"
GEMINI_SKILLS="${HOME}/.agent/skills"

echo "=== Installing TokenZero Engine ==="

# 1. Install CLI binary
mkdir -p "${TARGET_BIN}"
mkdir -p "${TARGET_LIB}"
cp "${REPO_DIR}/bin/tokenzero" "${TARGET_BIN}/tokenzero"
chmod +x "${TARGET_BIN}/tokenzero"
echo "[✓] Installed CLI binary to: ${TARGET_BIN}/tokenzero"

# 2. Install core library
cp -r "${REPO_DIR}/core" "${TARGET_LIB}/"
echo "[✓] Installed core ontology library to: ${TARGET_LIB}/core"

# 3. Deploy Skills
deploy_skill() {
    local target_dir="$1"
    if [ -d "$target_dir" ] || [ -d "$(dirname "$target_dir")" ]; then
        mkdir -p "${target_dir}/tokenzero"
        mkdir -p "${target_dir}/formula-first"
        mkdir -p "${target_dir}/laya-ultrafast"
        cp "${REPO_DIR}/skills/tokenzero/SKILL.md" "${target_dir}/tokenzero/SKILL.md"
        cp "${REPO_DIR}/skills/formula-first/SKILL.md" "${target_dir}/formula-first/SKILL.md"
        cp "${REPO_DIR}/skills/laya-ultrafast/SKILL.md" "${target_dir}/laya-ultrafast/SKILL.md"
        echo "[✓] Deployed skills to: ${target_dir}"
    fi
}

deploy_skill "${CLAUDE_SKILLS}"
deploy_skill "${CODEX_SKILLS}"
deploy_skill "${CODEX_SKILLS_V2}"
deploy_skill "${GEMINI_TEMPLATES}"
deploy_skill "${GEMINI_SKILLS}"

echo ""
echo "=== TokenZero Installation Complete ==="
if [[ ":$PATH:" != *":${TARGET_BIN}:"* ]]; then
    echo ""
    echo "[!] Notice: ${TARGET_BIN} is not in your PATH."
    echo "    Add it to your shell configuration (~/.zshrc or ~/.bashrc):"
    echo "    export PATH=\"\${HOME}/.local/bin:\$PATH\""
fi
echo "Verify with: tokenzero doctor"

