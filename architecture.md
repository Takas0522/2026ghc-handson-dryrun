# ポモドーロタイマー Web アプリケーション アーキテクチャ

## 概要

Flask + HTML/CSS/JavaScript によるポモドーロタイマー Web アプリケーション。  
タイマーのロジックはすべてクライアントサイド（JavaScript）で完結し、Flask はページ配信のみを担当するシンプルな構成。

---

## ディレクトリ構成

```
1.pomodoro/
├── app.py                      # Flask アプリケーション（エントリポイント）
├── static/
│   ├── css/
│   │   └── style.css           # スタイルシート
│   └── js/
│       ├── timer.js            # タイマーロジック（純粋なロジック層）
│       └── ui.js               # DOM操作層（UIバインディング）
├── templates/
│   └── index.html              # メインページテンプレート
└── tests/
    ├── test_app.py             # Flask ルーティングのテスト
    └── test_timer.js           # timer.js のユニットテスト
```

---

## 各レイヤーの責務

| レイヤー | ファイル | 責務 |
|---|---|---|
| **バックエンド** | `app.py` | Flask サーバー。ルーティング（`/` でページ配信） |
| **テンプレート** | `index.html` | Jinja2 テンプレート。UI構造の定義 |
| **スタイル** | `style.css` | UIモックに忠実なデザイン（円形プログレス、ボタン、カード等） |
| **ロジック層** | `timer.js` | タイマーの状態管理・時間計算・モード遷移（純粋関数） |
| **UI層** | `ui.js` | DOM操作・イベントリスナー・SVG更新 |
| **テスト** | `tests/` | Python / JavaScript のユニットテスト |

---

## 設計方針

### バックエンド（`app.py`）

- **アプリファクトリパターン**を採用し、テストごとに独立したアプリインスタンスを生成可能にする
- ルーティングは `GET /` のみ（SPA的にフロント側で完結）
- タイマーロジックはすべてクライアントサイドで処理するため、APIエンドポイントは基本不要

```python
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

### フロントエンド JavaScript

ロジック層（`timer.js`）と UI層（`ui.js`）を分離し、テスト容易性を確保する。

#### `timer.js`（ロジック層）

DOM に一切依存しない**純粋関数**の集合として設計する。

**状態オブジェクト:**

```javascript
function createInitialState() {
    return {
        mode: 'work',           // 'work' | 'break'
        timeRemaining: 25 * 60, // 秒
        isRunning: false,
        completedCount: 0,
        totalFocusTime: 0       // 秒
    };
}
```

**主要な純粋関数:**

| 関数 | 入力 | 出力 | テスト例 |
|---|---|---|---|
| `formatTime(seconds)` | 秒数 | `"25:00"` 形式の文字列 | `formatTime(1500) === "25:00"` |
| `tick(state)` | 現在の状態 | 1秒減算した新しい状態 | `tick({timeRemaining: 100}).timeRemaining === 99` |
| `completePomodoro(state)` | 現在の状態 | 完了数+1、集中時間加算した状態 | 完了数が1増えるか |
| `nextMode(state)` | 現在の状態 | 次のモード（作業↔休憩）の状態 | `work` → `break` に遷移するか |
| `resetTimer(mode)` | モード | 初期化された状態 | `resetTimer('work').timeRemaining === 1500` |
| `calcProgress(state)` | 現在の状態 | 0〜1 のプログレス値 | 半分経過時に `0.5` を返すか |

**タイマー関数の依存性注入:**

`setInterval` を外部から注入可能にし、テスト時にフェイクタイマーを差し込めるようにする。

```javascript
function startTimer(state, onTick, timerFn = setInterval) {
    return timerFn(() => onTick(tick(state)), 1000);
}
```

#### `ui.js`（UI層）

- DOM操作・イベントリスナーの登録
- `timer.js` の関数を呼び出して状態を更新し、結果をDOMに反映
- SVG プログレスリングの描画更新

### UI / CSS（`style.css`）

- **円形プログレスバー**: SVG `<circle>` + `stroke-dashoffset` で実装し、残り時間に応じてリングを更新
- **カラースキーム**: 紫系グラデーション背景（`#6C63FF` 系）
- **カード型レイアウト**: 中央配置、`border-radius` で丸みを持たせる
- **「今日の進捗」セクション**: 完了数と集中時間を表示するフッター領域

---

## データフロー

```
[ユーザー操作] → ui.js（イベント検知）→ timer.js（状態更新）→ ui.js（DOM更新）
     ↑                                                              |
     └───────────────── ボタンクリックイベント ────────────────────────┘
```

タイマーの全ロジックはブラウザ内で完結し、サーバーとの通信は初回ページロード時のみ。

---

## テスト戦略

### テスト種別

| テスト種別 | 対象 | ツール | カバー範囲 |
|---|---|---|---|
| **Python ユニットテスト** | `app.py`（ルーティング、レスポンス） | pytest + Flask test_client | バックエンド |
| **JS ユニットテスト** | `timer.js`（純粋関数群） | Jest または Vitest | タイマーロジック全般 |
| **手動 / E2E テスト** | `ui.js` + `index.html`（DOM連携） | ブラウザ目視 or Playwright | UI統合 |

### テスト容易性のための設計原則

| # | 原則 | 理由 |
|---|---|---|
| 1 | JS をロジック層（`timer.js`）と UI層（`ui.js`）に分離 | DOM非依存の純粋関数としてテスト可能にする |
| 2 | 状態をオブジェクトとして一元管理 | テストの Arrange を簡潔にし、状態遷移を検証しやすくする |
| 3 | 純粋関数として設計（副作用なし、入力→出力） | モック不要で直接テスト可能にする |
| 4 | `setInterval` 等の外部依存を注入可能にする | テスト時にフェイクタイマーを差し込める |
| 5 | Flask アプリファクトリパターンを採用 | テストごとに独立したアプリインスタンスを生成可能にする |

---

## UI仕様（モック準拠）

- **ヘッダー**: 「ポモドーロタイマー」タイトル + ウィンドウコントロール風装飾
- **モード表示**: 「作業中」/ 「休憩中」のテキスト
- **円形タイマー**: 中央に `MM:SS` 形式で残り時間を表示、外周にプログレスリング
- **操作ボタン**: 「開始」（塗りつぶし）/「リセット」（アウトライン）の2ボタン
- **今日の進捗カード**: 完了ポモドーロ数と合計集中時間を表示
- **自動遷移**: 作業25分 → 休憩5分 → 作業... を自動サイクル

---

## 拡張案（将来）

- **localStorage** で日次進捗を永続化し、ブラウザリロード後も復元
- **REST API** を追加してサーバー側にセッションデータを保存
- **長い休憩**: 4ポモドーロ完了後に15分休憩を挟むルール
- **通知**: タイマー完了時に `Notification API` やサウンドで通知
