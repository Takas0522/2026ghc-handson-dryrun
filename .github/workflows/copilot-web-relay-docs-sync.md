---
description: Detect code changes under 2.copilotWebRelay/ and update documentation to keep docs aligned with source code
on:
  push:
    branches: [main]
    paths:
      - "2.copilotWebRelay/**"
      - "!2.copilotWebRelay/docs/**"
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: read
  issues: read
tools:
  github:
safe-outputs:
  create-pull-request:
    title-prefix: "docs(copilotWebRelay): "
    labels: [documentation]
    draft: true
  noop:
---

# Copilot Web Relay Documentation Sync

You are an AI agent responsible for keeping the documentation under `2.copilotWebRelay/docs/` aligned with the source code under `2.copilotWebRelay/`.

## Your Task

When code changes are pushed to `2.copilotWebRelay/`, analyze the current source code and update the documentation to reflect the actual implementation.

## Steps

1. **Read the source code** under `2.copilotWebRelay/`:
   - `backend/main.py` — FastAPI アプリケーションのエントリポイント
   - `backend/cli_bridge.py` — Copilot CLI プロセス管理（PTY 制御）
   - `backend/websocket_handler.py` — WebSocket ハンドラ（メッセージルーティング + ステータス応答）
   - `backend/config.py` — 設定（dataclass で一元管理）
   - `backend/requirements.txt` — Python 依存関係
   - `frontend/src/` — React + TypeScript フロントエンドコード（App.tsx, main.tsx など）
   - `frontend/package.json` — フロントエンド依存関係
   - `frontend/vite.config.ts` — Vite 設定 + WebSocket プロキシ
   - `e2e/` — Playwright E2E テスト
   - `planning.md` — プロジェクト計画書

2. **Read the existing documentation** under `2.copilotWebRelay/docs/` (if any exists).

3. **Read existing design documents** for reference:
   - `2.copilotWebRelay/planning.md` — プロジェクト計画書（アーキテクチャ、機能要件、技術詳細）

4. **Compare and identify discrepancies** between the documentation and the actual source code:
   - WebSocket プロトコルの変更（メッセージ形式、新しいメッセージタイプ）
   - Backend API エンドポイントの追加・変更
   - CLI Bridge の動作フロー変更
   - フロントエンドコンポーネントの追加・変更
   - 設定パラメータの追加・変更
   - 依存関係の更新

5. **Update or create documentation files** under `2.copilotWebRelay/docs/`:
   - `2.copilotWebRelay/docs/architecture.md` — 現在のアーキテクチャ概要（コンポーネント構成、通信フロー、技術スタック）
   - `2.copilotWebRelay/docs/api-reference.md` — WebSocket プロトコル仕様 + REST API リファレンス（メッセージ形式、エンドポイント）
   - `2.copilotWebRelay/docs/backend.md` — バックエンドモジュール仕様（FastAPI, CLI Bridge, WebSocket ハンドラ）
   - `2.copilotWebRelay/docs/frontend.md` — フロントエンドモジュール仕様（React コンポーネント、状態管理、xterm.js 連携）
   - `2.copilotWebRelay/docs/setup.md` — 開発環境セットアップ手順、起動方法、依存関係

6. **Create a pull request** with the documentation updates using `create-pull-request` safe output.
   - Title: `docs(copilotWebRelay): sync documentation with latest code changes`
   - Body should summarize what documentation was updated and why.

## Guidelines

- Write documentation in Japanese (日本語) to match the existing project documentation style.
- Be precise and factual — only document what the code actually does, not what it should do.
- Include code examples where helpful (e.g., WebSocket message examples, API request/response examples).
- If there are no discrepancies and documentation is up to date, call the `noop` safe output with a clear message explaining that documentation is already in sync. This is important for transparency.
- Do NOT modify any source code — only update documentation files.
- Keep documentation concise and well-structured with clear headings.
- Pay special attention to the WebSocket protocol design, as it is the core communication mechanism between frontend and backend.
