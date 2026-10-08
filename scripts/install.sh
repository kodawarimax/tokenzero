#!/usr/bin/env bash
# ==============================================================================
# TokenZero Engine Universal Installer
# Compatible with macOS and Linux. Supports Claude Code, Codex, and Antigravity.
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_BIN="${HOME}/.local/bin"
TARGET_LIB="${HOME}/.local/lib/tokenzero"

echo "=========================================================="
echo "   Installing TokenZero Engine (Multi-Agent Kernel)      "
echo "=========================================================="
echo "Source: ${REPO_DIR}"
echo ""

# 1. ディレクトリの作成
mkdir -p "${TARGET_BIN}"
mkdir -p "${TARGET_LIB}"

# 2. Python パッケージおよびバイナリの配備
echo "[*] Installing Python modules and binary..."
cp -r "${REPO_DIR}/tokenzero" "${TARGET_LIB}/"
cp -r "${REPO_DIR}/core" "${TARGET_LIB}/"
cp "${REPO_DIR}/bin/tokenzero" "${TARGET_BIN}/tokenzero"
chmod +x "${TARGET_BIN}/tokenzero"
echo "    [✓] CLI Binary: ${TARGET_BIN}/tokenzero"
echo "    [✓] Library   : ${TARGET_LIB}/tokenzero"

# pip install (利用可能な場合)
if command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1; then
    PIP_CMD="$(command -v pip3 || command -v pip)"
    echo "[*] Registering package via ${PIP_CMD}..."
    "${PIP_CMD}" install -q -e "${REPO_DIR}" 2>/dev/null || true
fi

# 3. PATH 環境変数の自動検出・設定
PATH_NEEDS_UPDATE=false
if [[ ":$PATH:" != *":${TARGET_BIN}:"* ]]; then
    PATH_NEEDS_UPDATE=true
    SHELL_RC=""
    if [ -n "$ZSH_VERSION" ] || [ -f "${HOME}/.zshrc" ]; then
        SHELL_RC="${HOME}/.zshrc"
    elif [ -f "${HOME}/.bashrc" ]; then
        SHELL_RC="${HOME}/.bashrc"
    elif [ -f "${HOME}/.bash_profile" ]; then
        SHELL_RC="${HOME}/.bash_profile"
    fi

    if [ -n "$SHELL_RC" ]; then
        if ! grep -q '\.local/bin' "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo '# TokenZero CLI PATH' >> "$SHELL_RC"
            echo 'export PATH="${HOME}/.local/bin:$PATH"' >> "$SHELL_RC"
            echo "    [✓] Added ~/.local/bin to ${SHELL_RC}"
        fi
    fi
fi

# 4. 全AIエージェント環境へのスキル配備（Claude Code / Codex / Antigravity）
echo ""
echo "[*] Deploying skills to AI agents..."

deploy_skills() {
    local target_dir="$1"
    local agent_name="$2"
    mkdir -p "${target_dir}/tokenzero"
    mkdir -p "${target_dir}/formula-first"
    mkdir -p "${target_dir}/laya-ultrafast"
    
    cp "${REPO_DIR}/skills/tokenzero/SKILL.md" "${target_dir}/tokenzero/SKILL.md"
    cp "${REPO_DIR}/skills/formula-first/SKILL.md" "${target_dir}/formula-first/SKILL.md"
    cp "${REPO_DIR}/skills/laya-ultrafast/SKILL.md" "${target_dir}/laya-ultrafast/SKILL.md"
    echo "    [✓] ${agent_name} -> ${target_dir}"
}

# Claude Code
deploy_skills "${HOME}/.claude/skills" "Claude Code (Global)"

# Codex CLI
deploy_skills "${HOME}/.codex/skills" "Codex CLI (Global v2)"
deploy_skills "${HOME}/.agents/skills" "Codex CLI (Legacy)"

# Antigravity (Gemini)
deploy_skills "${HOME}/.gemini/antigravity/templates/skills" "Antigravity (Templates)"
deploy_skills "${HOME}/.agent/skills" "Antigravity (Workspace Global)"

# ワークスペース内にも存在する場合は更新
if [ -d "${PWD}/.agent/skills" ]; then
    deploy_skills "${PWD}/.agent/skills" "Current Workspace (.agent)"
fi
if [ -d "${PWD}/.claude/skills" ]; then
    deploy_skills "${PWD}/.claude/skills" "Current Workspace (.claude)"
fi

echo ""
echo "=========================================================="
echo "   Running Diagnostic Verification (tokenzero doctor)     "
echo "=========================================================="
export PATH="${TARGET_BIN}:${PATH}"
"${TARGET_BIN}/tokenzero" doctor

if [ "$PATH_NEEDS_UPDATE" = true ]; then
    echo "💡 Note: To use 'tokenzero' in your current terminal session, run:"
    echo "   source ${SHELL_RC:-~/.zshrc}"
    echo ""
fi

echo "TokenZero installation completed successfully!"
