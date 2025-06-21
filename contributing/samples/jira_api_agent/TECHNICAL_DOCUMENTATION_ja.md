# jira_mcp_agent - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`jira_mcp_agent` は、mcp-atlassian MCP サーバーと ADK の MCPToolset を活用したモダンな Jira 統合エージェントです。独自のAPI実装を排除し、MCP (Model Context Protocol) を通じて実績のある mcp-atlassian の機能を活用する設計パターンを実演します。

### 主要機能
- **MCP統合**: mcp-atlassian サーバーとのシームレス統合
- **ゼロカスタムコード**: Jira API の独自実装なし
- **包括的機能**: mcp-atlassian の全機能を継承
- **Docker統合**: コンテナ化された安全な実行環境
- **自動ツール発見**: MCP サーバーからの動的ツール取得

### 対象ユースケース
- 企業レベルの Jira 統合
- 保守性を重視したプロダクション環境
- MCP エコシステムの活用
- スケーラブルなAIエージェント開発

## 2. MCP アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (自然言語でのリクエスト)
[jira_mcp_agent] 
    ↓ (MCPToolset経由)
┌─────────────────────────────────────────────────────────┐
│ ADK MCPToolset (MCP Client)                             │
│ ├── MCP Protocol Handler                                │
│ ├── Tool Discovery & Registration                       │
│ ├── Docker Process Management                           │
│ └── Error Handling & Retry Logic                        │
└─────────────────────────────────────────────────────────┘
    ↓ (stdio/JSON-RPC)
┌─────────────────────────────────────────────────────────┐
│ mcp-atlassian (Docker Container)                        │
│ ├── Jira API Integration                                │
│ ├── Advanced Search & Filtering                         │
│ ├── Automated Issue Updates                             │
│ ├── Comment & Project Management                        │
│ └── Authentication Management                           │
└─────────────────────────────────────────────────────────┘
    ↓ (HTTPS/REST API)
[Jira Cloud]
    ├── Issues Database
    ├── Projects & Workflows
    ├── Users & Permissions
    └── Advanced Features
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス)
- **MCP統合**: MCPToolset + StdioServerParameters
- **外部サーバー**: mcp-atlassian Docker コンテナ
- **認証**: mcp-atlassian 経由の API Token 認証
- **プロセス管理**: Docker による分離実行

### MCP通信フロー
```python
1. Docker コンテナ起動
   └── mcp-atlassian サーバー初期化
2. MCPToolset 接続
   └── stdio パイプ経由でMCPサーバーと通信
3. ツール発見
   └── サーバーから利用可能ツール一覧を取得
4. ツール実行
   └── JSON-RPC プロトコルでツール呼び出し
5. レスポンス処理
   └── 結果をエージェントに返却
```

### 依存関係
```python
# ADK コアコンポーネント
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.base.external_tools.mcp import StdioServerParameters

# 設定管理
from dotenv import load_dotenv
import os
```

## 3. コード詳細解説

### 3.1 MCPToolset 統合

#### 環境変数の読み込みと検証
```python
load_dotenv()

# 設定の検証
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_USERNAME = os.getenv("JIRA_USERNAME", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
    raise ValueError(
        "必要な環境変数が不足しています。JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN を .env ファイルに設定してください。"
    )
```

#### MCPToolset の設定
```python
jira_mcp_tools = MCPToolset(
    connection_params=StdioServerParameters(
        command='docker',
        args=[
            'run', '--rm', '-i',
            '--env', f'JIRA_URL={JIRA_URL}',
            '--env', f'JIRA_USERNAME={JIRA_USERNAME}',
            '--env', f'JIRA_API_TOKEN={JIRA_API_TOKEN}',
            '-v', f'{os.path.expanduser("~")}/.mcp-atlassian:/home/app/.mcp-atlassian',
            'ghcr.io/sooperset/mcp-atlassian:latest'
        ]
    )
)
```

**設計の利点**:
- **分離実行**: Docker による安全な環境分離
- **自動管理**: MCPToolset が接続とプロセス管理を処理
- **拡張性**: 他の MCP サーバーの追加が容易

### 3.2 エージェント定義

#### シンプルなエージェント作成
```python
root_agent = Agent(
    name="jira_mcp_agent",
    model="gemini-2.0-flash",
    instruction="""あなたは mcp-atlassian を使用する Jira プロジェクト管理アシスタントです。

利用可能な機能:
1. Jira 課題の検索とフィルタリング
2. 課題の詳細情報取得
3. 新規課題の作成
4. 課題へのコメント追加
5. 課題の更新と状態変更
6. 高度なJQL (Jira Query Language) クエリ実行

使用可能なツールは mcp-atlassian によって提供され、以下のような操作が可能です:
- スマートな課題フィルタリング
- 自動的な課題更新
- プロジェクト情報の取得
- ユーザー情報の検索

常に明確で整理された情報を提供し、Jira の豊富な機能を活用してユーザーのプロジェクト管理を支援してください。
""",
    tools=[jira_mcp_tools],
)
```

**コードの特徴**:
- **簡潔性**: 78行の実装（従来の529行から85%削減）
- **ゼロカスタムAPI**: すべての機能は mcp-atlassian が提供
- **自動ツール発見**: MCPToolset が動的にツールを取得

## 4. 設定・環境構築

### 4.1 前提条件

#### 必須ソフトウェア
- Python 3.11+
- Docker (実行中)
- ADK (Agent Development Kit)

#### Docker の確認
```bash
# Docker のバージョン確認
docker --version

# Docker が実行中か確認
docker ps

# テスト実行
docker run --rm hello-world
```

### 4.2 Jira API Token の作成

#### API Token 生成手順
1. [Atlassian API tokens ページ](https://id.atlassian.com/manage-profile/security/api-tokens) にアクセス
2. "Create API token" をクリック
3. トークン名を入力（例："MCP Jira Agent"）
4. 生成されたトークンを即座にコピー（再表示されません）

### 4.3 環境設定

#### .env ファイルの作成
```bash
# プロジェクトディレクトリで .env ファイルを作成
cat > .env << EOF
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-generated-api-token
EOF
```

#### 環境変数の説明
- `JIRA_URL`: Jira Cloud インスタンスの URL
- `JIRA_USERNAME`: Jira アカウントのメールアドレス
- `JIRA_API_TOKEN`: 生成した API Token

### 4.4 実行方法

#### ADK Web インターフェース（推奨）
```bash
# Web UI での実行
adk web contributing/samples/jira_api_agent
```

#### 初回実行時の処理
1. Docker イメージの自動ダウンロード（mcp-atlassian）
2. mcp-atlassian サーバーの起動
3. MCPToolset による接続確立
4. 利用可能ツールの自動発見

## 5. MCP 統合の利点

### 5.1 従来実装との比較

#### コード量の削減
```
従来の実装:      529行（カスタムAPI実装）
新しい実装:      78行（MCPToolset使用）
削減率:          85%減
```

#### 保守性の向上
- **API変更対応**: mcp-atlassian の更新で自動対応
- **バグ修正**: 独自実装のバグ除去
- **機能拡張**: mcp-atlassian の新機能を自動継承

### 5.2 利用可能な高度機能

#### mcp-atlassian 提供機能
- **インテリジェント検索**: AI を活用した課題フィルタリング
- **自動課題更新**: テキストから課題への自動反映
- **リアルタイム同期**: Jira との即座の同期
- **高度なJQL**: 複雑なクエリの簡単実行

### 5.3 拡張パターン

#### 他の MCP サーバーとの組み合わせ
```python
# 複数のMCPサーバーを組み合わせた例
enhanced_agent = Agent(
    name="multi_mcp_agent",
    model="gemini-2.0-flash",
    tools=[
        jira_mcp_tools,              # Jira 統合
        # confluence_mcp_tools,      # Confluence 統合
        # slack_mcp_tools,           # Slack 統合
        # filesystem_mcp_tools,      # ファイルシステム
    ],
    instruction="複数のサービスを統合したワークフロー自動化エージェント"
)
```

#### カスタム設定の追加
```python
# Docker 引数のカスタマイズ例
custom_jira_tools = MCPToolset(
    connection_params=StdioServerParameters(
        command='docker',
        args=[
            'run', '--rm', '-i',
            '--env', f'JIRA_URL={JIRA_URL}',
            '--env', f'JIRA_USERNAME={JIRA_USERNAME}',
            '--env', f'JIRA_API_TOKEN={JIRA_API_TOKEN}',
            # プロキシ設定の追加
            '--env', 'HTTP_PROXY=http://proxy.company.com:8080',
            # メモリ制限
            '--memory', '512m',
            # 設定ファイルマウント
            '-v', f'{os.path.expanduser("~")}/.mcp-atlassian:/home/app/.mcp-atlassian',
            'ghcr.io/sooperset/mcp-atlassian:latest'
        ]
    )
)
```

## 6. トラブルシューティング

### 6.1 Docker 関連のエラー

#### Docker が見つからない
```bash
# Docker のインストール確認
docker --version

# Docker デーモンの状態確認
docker info
```

#### mcp-atlassian イメージのダウンロード失敗
```bash
# 手動でイメージをダウンロード
docker pull ghcr.io/sooperset/mcp-atlassian:latest

# ネットワーク接続の確認
curl -I https://ghcr.io
```

### 6.2 MCP 接続エラー

#### MCP サーバーとの通信失敗
- **原因**: Docker コンテナの起動失敗
- **解決法**: Docker ログの確認
```bash
# コンテナログの確認
docker logs $(docker ps -q --filter ancestor=ghcr.io/sooperset/mcp-atlassian:latest)
```

#### 環境変数が認識されない
- **原因**: 環境変数の設定ミス
- **解決法**: .env ファイルの確認
```bash
# 環境変数の確認
cat .env
# JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN の確認
```

### 6.3 認証エラー

#### API Token 認証失敗
```bash
# API Token の手動テスト
curl -u "your-email@example.com:your-api-token" \
  https://your-domain.atlassian.net/rest/api/3/myself
```

#### 権限不足エラー
- Jira Web UI でプロジェクトアクセス権を確認
- API Token の権限スコープを確認

## 7. 設計哲学とベストプラクティス

### 7.1 MCP 統合パターン

#### ゼロカスタムコード原則
```python
# ❌ 避けるべきパターン（カスタムAPI実装）
def custom_jira_search(jql: str):
    # 数百行のカスタム実装...
    pass

# ✅ 推奨パターン（MCP統合）
jira_tools = MCPToolset(connection_params=...)
agent = Agent(tools=[jira_tools])
```

#### 分離実行の利点
- **セキュリティ**: Docker による環境分離
- **保守性**: mcp-atlassian の更新で自動改善
- **拡張性**: 他の MCP サーバーとの組み合わせ

### 7.2 MCP エコシステムの活用

#### 複数サービス統合
```python
# Jira + Confluence + Slack の統合例
multi_service_agent = Agent(
    tools=[
        jira_mcp_tools,
        confluence_mcp_tools,
        slack_mcp_tools,
    ]
)
```

### 7.3 開発効率の向上

#### 実装時間の短縮
- 従来: 数週間のAPI実装開発
- MCP統合: 数時間の設定のみ

#### 保守コストの削減
- API変更への自動対応
- バグ修正の自動適用
- 機能拡張の自動継承

この jira_mcp_agent は、MCP エコシステムを活用したモダンな統合パターンを実演し、保守性と拡張性を重視した実用的な実装例を提供します。