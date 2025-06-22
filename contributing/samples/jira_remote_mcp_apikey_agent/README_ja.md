# Jira Remote MCP API キーエージェント

このエージェントは、API キー認証を使用して Atlassian のリモート MCP (Model Context Protocol) サーバーに接続し、Jira Cloud と対話します。

## 特徴

- Atlassian の MCP サーバーへの直接接続（ローカル Docker 不要）
- シンプルな API キー認証
- MCP を通じて公開される全ての Jira 操作へのアクセス
- 自動エラーハンドリングとリトライロジック
- 環境変数による安全な認証情報管理

## 前提条件

1. **Jira Cloud アカウント**: Jira Cloud インスタンスが必要（Server/Data Center ではない）
2. **Atlassian API トークン**: [Atlassian アカウント設定](https://id.atlassian.com/manage-profile/security/api-tokens)から生成
3. **Python 3.10+**: MCP サポートに必要

## セットアップ

1. **環境変数テンプレートをコピー**:
   ```bash
   cp .env.example .env
   ```

2. **`.env` ファイルに認証情報を設定**:
   ```env
   JIRA_DOMAIN=your-company.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token-here
   ```

3. **依存関係をインストール** (単体実行の場合):
   ```bash
   pip install google-adk[mcp]
   ```

## 使用方法

### ADK CLI を使用

```bash
# エージェントを実行
adk run path/to/jira_remote_mcp_apikey_agent

# または Web インターフェースを使用
adk web path/to/jira_remote_mcp_apikey_agent
```

### モジュールとして使用

```python
from jira_remote_mcp_apikey_agent import agent

# エージェントは事前設定済みですぐに使用可能
response = await agent.say("プロジェクト ABC に新しいバグ課題を作成して")
```

## 利用可能な操作

このエージェントは、Atlassian の MCP サーバーが提供する全ての Jira 操作にアクセスできます：

- **課題管理**: 課題の作成、更新、削除、遷移
- **検索**: JQL クエリの実行、課題検索
- **プロジェクト**: プロジェクト一覧、プロジェクト詳細取得
- **ユーザー**: ユーザー検索、ユーザー詳細取得
- **ワークフロー**: 利用可能な遷移取得、課題移動
- **フィールド**: フィールド設定、カスタムフィールド取得
- **コメント**: コメントの追加、更新、削除
- **添付ファイル**: ファイルのアップロードと管理

## セキュリティ注意事項

- API トークンは環境変数で保存（`.env` ファイルをコミットしない）
- 全通信で HTTPS を使用
- Basic Auth ヘッダーは email:token から自動生成
- レスポンスにトークンはログ出力や表示されない

## トラブルシューティング

### 認証エラー
- API トークンが有効で期限切れでないことを確認
- メールアドレスが Atlassian アカウントと一致することを確認
- Jira インスタンスが API アクセスを許可していることを確認

### 接続問題
- インターネット接続があることを確認
- `https://mcp.atlassian.com` にアクセス可能か確認
- `JIRA_CONNECTION_TIMEOUT` の値を増やしてみる

### ツールが見つからない
- 一部のツールは特定の Jira 権限が必要な場合がある
- アカウントに必要なアクセス権があることを確認

## 使用例

```
ユーザー: プロジェクト XYZ の全ての未解決バグを一覧表示して
エージェント: JQL を使用してプロジェクト XYZ の未解決バグを検索します...

ユーザー: ドキュメント更新用の新しいタスクを作成して
エージェント: ドキュメント更新用の新しいタスク課題を作成します。どのプロジェクトに作成しますか？

ユーザー: 私に割り当てられた課題を表示して
エージェント: 現在あなたに割り当てられている全ての課題を検索します...
```

## 高度な設定

### カスタム MCP サーバー URL

異なる MCP エンドポイントを使用する場合:
```env
JIRA_MCP_SERVER_URL=https://custom-mcp-server.com/v1/sse
```

### 接続タイムアウト

低速接続でのタイムアウト調整:
```env
JIRA_CONNECTION_TIMEOUT=60  # 秒
```

## 制限事項

- インターネット接続が必要（オフラインモード不可）
- Atlassian API レート制限の対象
- 一部の高度な Jira 機能は MCP 経由で公開されていない場合がある
- Jira Server/Data Center にはアクセス不可（Cloud のみ）

## 関連項目

- [Jira Remote MCP OAuth2 Agent](../jira_remote_mcp_oauth2_agent/) - OAuth2 認証用
- [Atlassian API ドキュメント](https://developer.atlassian.com/cloud/jira/platform/)
- [MCP プロトコル仕様](https://modelcontextprotocol.io/)