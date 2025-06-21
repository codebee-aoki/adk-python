# Jira MCP Agent

MCP Atlassian サーバーと ADK の MCPToolset を使用したモダンな Jira 統合エージェントです。このエージェントは独自実装なしで mcp-atlassian の力を活用し、Model Context Protocol を通じて包括的な Jira 機能を提供します。

## 機能

- **高度な課題検索**: インテリジェントな課題フィルタリングと JQL クエリ実行
- **課題管理**: 完全なフィールドサポートでの課題作成、更新、管理
- **コメント管理**: 課題へのコメント追加と管理
- **プロジェクト情報**: 詳細なプロジェクトとユーザー情報へのアクセス
- **スマートフィルタリング**: AI を活用した課題フィルタリング機能
- **リアルタイム統合**: MCP Atlassian を通じた Jira への直接接続

## 前提条件

- Python 3.11+
- ADK (Agent Development Kit) がインストール済み
- Docker がインストールされ、実行中
- API token を持つ Jira Cloud アカウント
- Jira プロジェクトへのアクセス権

## セットアップ

### 1. Jira API Token の生成

1. [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens) にアクセス
2. "Create API token" をクリック
3. 分かりやすい名前を付ける（例："MCP Jira Agent"）
4. 生成されたトークンを即座にコピー（再表示されません）

### 2. 環境変数の設定

このディレクトリに `.env` ファイルを作成してください：

```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
```

**必須変数:**
- `JIRA_URL`: あなたの Jira Cloud インスタンス URL
- `JIRA_USERNAME`: あなたの Jira アカウントのメールアドレス
- `JIRA_API_TOKEN`: ステップ1で生成された API token

### 3. Docker インストールの確認

Docker がインストールされ、実行中であることを確認してください：

```bash
docker --version
docker run --rm hello-world
```

## 使用方法

### ADK Web インターフェースでの実行

```bash
# Web インターフェースを起動（推奨）
adk web contributing/samples/jira_api_agent
```

これにより ADK Web インターフェースが開始され、チャットインターフェースを通じて Jira エージェントと対話できます。

### 使用例

#### 課題の検索

```
User: "プロジェクト PROJ のすべてのオープン課題を検索してください"
Agent: *mcp-atlassian ツールを使用してスマートフィルタリング*
```

```
User: "先週の緊急バグを見つけてください"
Agent: *mcp-atlassian のインテリジェントフィルタリング機能を活用*
```

#### 課題詳細の取得

```
User: "PROJ-123 の詳細を教えてください"
Agent: *MCP Atlassian を通じて包括的な課題情報を取得*
```

#### 新規課題の作成

```
User: "ログイン問題のバグレポートを作成してください"
Agent: *mcp-atlassian の作成ツールを使用して課題を作成*
```

#### ミーティングノートからの課題更新

```
User: "ミーティングノートから Jira を更新してください"
Agent: *mcp-atlassian の自動課題更新機能を使用*
```

## 仕組み

このエージェントは [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) MCP サーバーを活用し、以下を提供します：

- **Docker ベース統合**: Docker コンテナで mcp-atlassian サーバーを実行
- **MCPToolset 接続**: ADK の MCPToolset を使用してサーバーに接続
- **ゼロカスタムコード**: カスタム Jira API 実装は不要
- **豊富な機能**: mcp-atlassian のすべての機能にアクセス

## 利用可能なツール

エージェントは mcp-atlassian によって提供されるすべてのツールを自動的に受信します：

### Jira ツール
- スマートな課題検索とフィルタリング
- 完全なフィールドサポートでの課題作成
- 課題の更新とステータス変更
- コメント管理
- プロジェクト情報の取得
- ユーザーと権限の管理

### 高度な機能
- JQL クエリ実行
- テキストからの自動課題更新
- インテリジェントコンテンツフィルタリング
- リアルタイム同期

## セキュリティ考慮事項

- **API Token の保存**: `.env` ファイルをコミットしたり API token を露出させたりしないでください
- **Docker セキュリティ**: Docker デーモンが適切にセキュアされていることを確認してください
- **権限**: エージェントは API token 所有者の権限を継承します
- **コンテナ分離**: mcp-atlassian は分離された Docker コンテナで実行されます
- **データプライバシー**: 機密性の高い課題データを扱う際は注意してください

## トラブルシューティング

### Docker 問題
- Docker がインストールされ実行中であることを確認: `docker --version`
- Docker デーモンにアクセス可能であることを確認: `docker ps`
- Docker イメージのための十分なディスク容量を確保

### 認証失敗
- API token が正しく、期限切れでないことを確認してください
- メールアドレスが Jira アカウントと一致することを確認してください
- Jira URL が正しいサブドメインを含むことを確認してください
- 認証情報を手動でテスト: `curl -u email:token https://your-domain.atlassian.net/rest/api/3/myself`

### MCP 接続問題
- mcp-atlassian の Docker コンテナログを確認
- 環境変数がコンテナに正しく渡されていることを確認
- ADK と Docker コンテナ間のネットワーク接続を確認

### 権限エラー
- アカウントがプロジェクトにアクセスできることを確認してください
- Jira 設定でプロジェクト権限を確認してください
- 一部の操作には管理者権限が必要な場合があります

## 技術アーキテクチャ

このエージェントは API 統合への最新のアプローチを実演します：

1. **MCPToolset**: ADK の MCP クライアントが外部 MCP サーバーに接続
2. **mcp-atlassian**: Jira 統合を提供する Docker ベース MCP サーバー
3. **ゼロカスタムコード**: カスタム API 実装は不要
4. **拡張可能**: 追加機能のために他の MCP サーバーを簡単に追加可能

## 利点

- **簡素化されたメンテナンス**: メンテナンスすべきカスタム API コードなし
- **豊富な機能**: mcp-atlassian の機能にフルアクセス
- **将来性**: mcp-atlassian の改善時に自動更新
- **ベストプラクティス**: 実戦でテストされた mcp-atlassian 実装を活用

## 関連ドキュメント

- [mcp-atlassian GitHub](https://github.com/sooperset/mcp-atlassian)
- [MCP ドキュメント](https://modelcontextprotocol.io/)
- [ADK MCP ツール](https://google.github.io/adk-docs/tools/mcp-tools/)
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [ADK ドキュメント](https://github.com/google/adk-python)