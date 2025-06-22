# Jira Remote MCP OAuth2 エージェント

このエージェントは、OAuth2 認証を使用して Atlassian のリモート MCP (Model Context Protocol) サーバーに接続し、Jira Cloud と対話します。自動トークンリフレッシュとセキュアストレージによるエンタープライズグレードのセキュリティを提供します。

## 特徴

- PKCE (Proof Key for Code Exchange) 付き OAuth2 認証
- アクセストークン期限切れ時の自動トークンリフレッシュ
- セキュアなローカルトークンストレージ
- Atlassian の MCP サーバーへの直接接続（Docker 不要）
- MCP を通じて公開される全ての Jira 操作へのアクセス
- マルチテナントサポート（複数の Jira インスタンスで動作可能）

## 前提条件

1. **Jira Cloud アカウント**: Jira Cloud インスタンスが必要（Server/Data Center ではない）
2. **Atlassian OAuth2 アプリ**: [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/) で作成
3. **Python 3.10+**: MCP サポートに必要

## OAuth2 アプリのセットアップ

1. [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/) にアクセス
2. 「Create new app」をクリック
3. アプリを設定：
   - **アプリ名**: 分かりやすい名前を選択
   - **アプリ説明**: 統合の簡単な説明
   - **アプリタイプ**: 「OAuth 2.0 integration」を選択
4. OAuth2 を設定：
   - **コールバック URL**: `http://localhost:8080/callback`（またはカスタム URL）
   - **権限**: 必要なスコープを追加：
     - `read:jira-work`
     - `write:jira-work`  
     - `read:jira-user`
     - `offline_access`（リフレッシュトークン用）
5. **クライアント ID** と **クライアントシークレット** を保存

## エージェントのセットアップ

1. **環境変数テンプレートをコピー**:
   ```bash
   cp .env.example .env
   ```

2. **`.env` ファイルに認証情報を設定**:
   ```env
   JIRA_DOMAIN=your-company.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_OAUTH_CLIENT_ID=your-oauth-client-id
   JIRA_OAUTH_CLIENT_SECRET=your-oauth-client-secret
   JIRA_OAUTH_REDIRECT_URI=http://localhost:8080/callback
   ```

3. **依存関係をインストール** (単体実行の場合):
   ```bash
   pip install google-adk[mcp] aiohttp
   ```

## 使用方法

### 初回実行（認証）

初回実行時、エージェントは：
1. ポート 8080 でローカル Web サーバーを開始
2. ブラウザで Atlassian の OAuth2 同意ページを開く
3. 認証後、今後の使用のためにトークンを安全に保存

### ADK CLI を使用

```bash
# エージェントを実行
adk run path/to/jira_remote_mcp_oauth2_agent

# または Web インターフェースを使用
adk web path/to/jira_remote_mcp_oauth2_agent
```

### モジュールとして使用

```python
from jira_remote_mcp_oauth2_agent import agent

# エージェントは OAuth2 フローを自動処理
response = await agent.say("高優先度のバグを全て表示して")
```

## トークン管理

### トークンストレージ
- トークンは `~/.jira_mcp_tokens/` に制限的権限で保存
- 各 Jira ドメインが独自のトークンファイルを持つ
- トークンは期限切れ時に自動的にリフレッシュ

### 手動トークン管理
```bash
# 保存されたトークンを表示（注意 - 機密データを含む！）
ls -la ~/.jira_mcp_tokens/

# 特定ドメインのトークンを削除
rm ~/.jira_mcp_tokens/your_company_atlassian_net.json
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

## セキュリティ機能

### PKCE 付き OAuth2
- セキュリティ強化のため Authorization Code フローと PKCE を使用
- アプリにクライアント認証情報が保存されない
- CSRF 攻撃を防ぐ state パラメータ

### トークンセキュリティ
- アクセストークンは短い有効期限（通常1時間）
- リフレッシュトークンにより再認証なしで自動更新
- トークンは制限的ファイル権限（600）で保存
- トークンファイルは所有者のみアクセス可能

### ベストプラクティス
- `.env` ファイルやトークンファイルを共有しない
- OAuth2 クライアントシークレットを定期的にローテーション
- Atlassian 設定でアプリ権限を確認
- 開発/本番で環境固有の OAuth2 アプリを使用

## トラブルシューティング

### OAuth2 フロー問題

**ブラウザが自動で開かない**:
- コンソールに表示された URL に手動でアクセス
- システムがターミナルからのブラウザ起動を許可していることを確認

**コールバックが失敗**:
- ポート 8080 が使用されていないことを確認
- リダイレクト URI が OAuth2 アプリ設定と一致することを確認
- `OAUTH_CALLBACK_PORT` で別のポートを試す

**認証拒否**:
- 正しい Atlassian アカウントにログインしていることを確認
- OAuth2 アプリが必要な権限を持っていることを確認
- Jira ドメインが認証済みサイトと一致することを確認

### トークン問題

**トークンリフレッシュ失敗**:
- トークンファイルを削除して再認証
- OAuth2 アプリがまだ `offline_access` スコープを持っていることを確認
- クライアントシークレットがローテーションされていないか確認

**認証後のアクセス拒否**:
- アカウントが Jira アクセス権を持っていることを確認
- Jira サイトがアクセス可能リソースに含まれていることを確認
- OAuth2 アプリが停止されていないか確認

### 接続問題
- インターネット接続を確認
- `https://mcp.atlassian.com` にアクセス可能か確認
- プロキシ/ファイアウォール設定を確認

## 使用例

```
ユーザー: アクセス可能な Jira プロジェクトは何ですか？
エージェント: アクセス可能な全ての Jira プロジェクトを一覧表示します...

ユーザー: ログインページが動作しないバグを作成して
エージェント: バグ課題を作成します。どのプロジェクトに作成し、どのような詳細を含めますか？

ユーザー: 今週作成した全ての課題を表示して
エージェント: JQL を使用して今週あなたが作成した全ての課題を検索します...
```

## 高度な設定

### カスタムコールバックポート

ポート 8080 が使用中の場合:
```env
OAUTH_CALLBACK_PORT=8888
JIRA_OAUTH_REDIRECT_URI=http://localhost:8888/callback
```

### カスタムトークンストレージ場所

環境変数を設定:
```env
JIRA_TOKEN_STORAGE_PATH=/custom/path/to/tokens
```

### プロキシ設定

企業環境用:
```env
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

## API キーエージェントとの比較

| 機能 | OAuth2 エージェント | API キーエージェント |
|------|------------------|---------------------|
| セキュリティ | 高い（トークン期限切れ） | 低い（永続キー） |
| セットアップ複雑さ | 高い（OAuth2 アプリ） | 低い（API キーのみ） |
| トークン管理 | 自動リフレッシュ | 不要 |
| ユーザー属性 | 完全なユーザーコンテキスト | サービスアカウント |
| エンタープライズ対応 | はい | 限定的 |
| マルチテナント | はい | キーごとに基づく |

## 関連項目

- [Jira Remote MCP API Key Agent](../jira_remote_mcp_apikey_agent/) - よりシンプルな認証オプション
- [Atlassian OAuth2 ドキュメント](https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/)
- [MCP プロトコル仕様](https://modelcontextprotocol.io/)