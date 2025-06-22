# Jira Remote MCP 共通ユーティリティ

このディレクトリには、API キーと OAuth2 の両方の Jira Remote MCP エージェントで使用される共有ユーティリティが含まれています。

## 構成

- `config.py` - Jira 接続用の設定管理
- `auth.py` - 認証ヘッダー作成（Basic Auth と Bearer トークン）
- `errors.py` - 共通エラーハンドリングとロギング設定
- `test_connection.py` - MCP サーバー接続をテストするユーティリティ
- `__init__.py` - パッケージ初期化

## MCP 接続テスト

`test_connection.py` スクリプトを使用して、Atlassian の MCP サーバーへの接続を確認し、利用可能なツールを発見できます。

### 使用方法

1. 環境変数を設定：
   ```bash
   export JIRA_DOMAIN=your-company.atlassian.net
   export JIRA_EMAIL=your-email@example.com
   export JIRA_API_TOKEN=your-api-token
   ```

2. テストスクリプトを実行：
   ```bash
   cd jira_remote_mcp_common
   python test_connection.py
   ```

3. 期待される出力：
   - 接続ステータス
   - 利用可能な MCP ツールの一覧
   - `jira_get_myself` のテスト呼び出し（利用可能な場合）

### テストで判明すること

テストスクリプトは以下を表示します：
- 認証情報が有効かどうか
- MCP 経由で利用可能な全ての Jira 操作
- 各ツールの入力スキーマ
- 現在のユーザー情報

これは以下の用途に役立ちます：
- エージェント使用前のセットアップ確認
- 利用可能な操作の理解
- 認証問題のデバッグ
- MCP ツールスキーマの探索

## 共有コンポーネント

### JiraConfig

集中化された設定クラスで以下を処理：
- 環境変数からの読み込み
- 異なる認証方法のバリデーション
- MCP サーバー URL のデフォルト値

### 認証ヘルパー

- `create_basic_auth_header()` - API キー認証用
- `create_bearer_auth_header()` - OAuth2 トークン認証用

### エラーハンドリング

両エージェント間で一貫したエラータイプとロギング：
- `JiraMCPError` - ベースエラークラス
- `AuthenticationError` - 認証失敗
- `ConnectionError` - ネットワーク問題
- `ConfigurationError` - 設定不足/無効

## 環境変数

両エージェントで使用される共通変数：

| 変数 | 説明 | 必須 |
|------|------|------|
| `JIRA_DOMAIN` | Jira Cloud ドメイン（例：company.atlassian.net） | はい |
| `JIRA_EMAIL` | Atlassian アカウントメール | はい |
| `JIRA_API_TOKEN` | Basic Auth 用 API トークン | API キーエージェント用 |
| `JIRA_OAUTH_CLIENT_ID` | OAuth2 クライアント ID | OAuth2 エージェント用 |
| `JIRA_OAUTH_CLIENT_SECRET` | OAuth2 クライアントシークレット | OAuth2 エージェント用 |
| `JIRA_MCP_SERVER_URL` | MCP サーバー URL のオーバーライド | いいえ |
| `JIRA_CONNECTION_TIMEOUT` | 接続タイムアウト（秒） | いいえ |

## セキュリティ注意事項

- 実際の認証情報を含む `.env` ファイルをコミットしない
- API トークンと OAuth2 シークレットを安全に保管
- 本番環境では環境変数またはセキュアボルトを使用
- ユーティリティは機密データがログに記録されないことを保証