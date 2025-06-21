# MCP Atlassian Authentication Guide

このドキュメントは、[MCP Atlassian](https://github.com/sooperset/mcp-atlassian) プロジェクトの Quick Start Guide における認証設定の Pattern A と Pattern C について詳細に記録したものです。

## 概要

MCP Atlassian は、Atlassian Cloud サービス（Jira、Confluence）に接続するための MCP（Model Context Protocol）サーバーです。このツールを使用するためには、適切な認証設定が必要で、主に以下の2つのパターンが提供されています：

- **Pattern A**: API Token Authentication (推奨)
- **Pattern C**: OAuth 2.0 Authentication (高度な設定)

## Pattern A: API Token Authentication (Cloud) - 推奨方法

### 概要
API Token 認証は最もシンプルで推奨される認証方法です。個人のアカウントに関連付けられたトークンを使用して認証を行います。

### セットアップ手順

#### 1. API Token の作成
1. [Atlassian API Token 管理ページ](https://id.atlassian.com/manage-profile/security/api-tokens) にアクセス
2. "Create API token" をクリック
3. トークンに適切な名前を付ける（例：`MCP-Atlassian-Integration`）
4. 生成されたトークンを **即座にコピー** する（再表示されません）

#### 2. 環境変数の設定

**Confluence 用:**
```bash
export CONFLUENCE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-generated-api-token"
```

**Jira 用:**
```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-generated-api-token"
```

#### 3. 設定ファイル例

`.env` ファイルに保存する場合：
```env
# Confluence Settings
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-generated-api-token

# Jira Settings
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-generated-api-token
```

### 利点
- **簡単な設定**: 数分で完了
- **直接的**: 複雑な OAuth フローが不要
- **即座に利用可能**: トークン生成後すぐに使用開始
- **デバッグが容易**: シンプルな認証フロー

### 適用ケース
- 個人での使用
- プロトタイプ開発
- 小規模チームでの利用
- 迅速な概念実証（PoC）

### セキュリティ考慮事項
- API トークンは個人アカウントに紐づく
- トークンの有効期限なし（手動での取り消しが必要）
- 適切な権限スコープの管理が重要

## Pattern C: OAuth 2.0 Authentication (Cloud) - 高度な方法

### 概要
OAuth 2.0 認証は、より堅牢なセキュリティを提供する高度な認証方法です。アプリケーションレベルでの認証を可能にし、細かい権限制御とトークンの自動更新を提供します。

### セットアップ手順

#### 1. Atlassian Developer Console での OAuth アプリ作成

1. [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/) にアクセス
2. "Create" → "OAuth 2.0 (3LO) integration" を選択
3. アプリケーション情報を入力：
   - App name: `MCP Atlassian Integration`
   - App description: 適切な説明を記入

#### 2. OAuth アプリの設定

**権限（Scopes）の設定:**

Jira 用権限：
- `read:jira-user`
- `read:jira-work`
- `write:jira-work`
- `offline_access` （重要：トークン更新のため）

Confluence 用権限：
- `read:confluence-content.all`
- `write:confluence-content`
- `read:confluence-space.summary`
- `offline_access`

**Callback URL の設定:**
```
http://localhost:8080/callback
```

#### 3. OAuth セットアップウィザードの実行

Docker を使用したセットアップ：
```bash
docker run --rm -i \
  -p 8080:8080 \
  -v "${HOME}/.mcp-atlassian:/home/app/.mcp-atlassian" \
  ghcr.io/sooperset/mcp-atlassian:latest --oauth-setup -v
```

#### 4. 対話式セットアップ

ウィザードが以下の情報を要求します：
1. **Client ID**: Developer Console から取得
2. **Client Secret**: Developer Console から取得
3. **Redirect URI**: `http://localhost:8080/callback`
4. **Scope**: 前述の権限を組み合わせた文字列

例：
```
read:jira-user read:jira-work write:jira-work read:confluence-content.all write:confluence-content read:confluence-space.summary offline_access
```

#### 5. ブラウザでの認証

1. ウィザードがローカルサーバーを起動
2. ブラウザで認証 URL にアクセス
3. Atlassian でログイン・認証
4. 自動的に認証情報が保存される

#### 6. 環境変数の設定

認証完了後、以下の環境変数が使用可能：
```bash
export ATLASSIAN_OAUTH_CLOUD_ID="your-cloud-id"
export ATLASSIAN_OAUTH_CLIENT_ID="your-client-id"
export ATLASSIAN_OAUTH_CLIENT_SECRET="your-client-secret"
export ATLASSIAN_OAUTH_REDIRECT_URI="http://localhost:8080/callback"
export ATLASSIAN_OAUTH_SCOPE="read:jira-user read:jira-work write:jira-work read:confluence-content.all write:confluence-content read:confluence-space.summary offline_access"
```

### 利点
- **強化されたセキュリティ**: アプリケーションレベルでの認証
- **細かい権限制御**: 必要最小限の権限のみ付与
- **トークンの自動更新**: `offline_access` による継続的なアクセス
- **監査可能**: アプリケーションごとのアクセス履歴
- **企業利用に適合**: 組織のセキュリティポリシーに準拠

### 適用ケース
- エンタープライズ環境
- 本番環境での利用
- 複数ユーザーでの共有アプリケーション
- 高いセキュリティ要件が必要なケース

### セキュリティ考慮事項
- Client Secret の適切な管理
- Scope の最小権限原則
- トークンの定期的なローテーション
- アクセスログの監視

## 認証パターンの比較と選択ガイド

### 比較表

| 項目 | Pattern A (API Token) | Pattern C (OAuth 2.0) |
|------|----------------------|----------------------|
| **設定の複雑さ** | 簡単 | 複雑 |
| **設定時間** | 5分以内 | 15-30分 |
| **セキュリティレベル** | 基本 | 高度 |
| **権限制御** | ユーザー権限に依存 | 細かく制御可能 |
| **トークン更新** | 手動 | 自動 |
| **企業利用適性** | 限定的 | 高い |
| **デバッグ容易さ** | 易しい | やや複雑 |
| **監査機能** | 限定的 | 詳細 |

### 選択指針

**Pattern A を選ぶべき場合:**
- 個人開発やプロトタイプ
- 迅速な概念実証が必要
- シンプルな統合で十分
- 小規模チームでの使用

**Pattern C を選ぶべき場合:**
- 本番環境での利用
- 企業・組織での利用
- 高いセキュリティ要件
- 複数ユーザーでの共有
- 詳細な監査ログが必要

### セキュリティのベストプラクティス

#### 共通事項
- 認証情報の環境変数での管理
- `.env` ファイルの `.gitignore` への追加
- 定期的な認証情報のローテーション

#### API Token 利用時
- トークンの適切な命名
- 不要になったトークンの即座な削除
- アクセス権限の定期的な見直し

#### OAuth 2.0 利用時
- Client Secret の暗号化保存
- Scope の最小権限原則の適用
- アクセストークンの適切な有効期限設定

## まとめ

MCP Atlassian の認証設定において、Pattern A（API Token）は簡単で迅速な実装が可能で、個人利用や小規模プロジェクトに適しています。一方、Pattern C（OAuth 2.0）はより高度なセキュリティと柔軟性を提供し、企業環境や本番利用に適しています。

プロジェクトの要件、セキュリティポリシー、利用規模を考慮して適切な認証パターンを選択することが重要です。