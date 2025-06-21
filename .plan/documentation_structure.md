# ADK サンプルエージェント ドキュメンテーション構造

## 全体構造概要

この計画では、contributing/samples 配下の全42エージェントに対して、プログラマー向けの詳細技術ドキュメントを作成します。

## エージェント分類

### 1. 基本/チュートリアル系 (7エージェント)
- **hello_world** - カスタムツール関数の基本例
- **hello_world_anthropic** - Anthropic モデル使用例
- **hello_world_litellm** - LiteLLM 統合例
- **hello_world_ollama** - Ollama ローカルモデル例
- **hello_world_ma** - マルチエージェント基本例
- **quickstart** - クイックスタート例
- **artifact_save_text** - テキストアーティファクト管理

### 2. Google サービス統合系 (4エージェント)
- **bigquery** - BigQuery 統合と認証
- **bigquery_agent** - BigQuery エージェント実装
- **google_search_agent** - Google 検索統合
- **oauth_calendar_agent** - OAuth ベース Google Calendar 統合

### 3. 外部API統合系 (3エージェント)
- **jira_agent** - JIRA 統合 (Application Integration Toolset)
- **integration_connector_euc_agent** - エンタープライズ統合コネクタ
- **application_integration_agent** - 汎用アプリケーション統合

### 4. マルチエージェント アーキテクチャ系 (4エージェント)
- **workflow_agent_seq** - SequentialAgent によるコード作成パイプライン
- **simple_sequential_agent** - 基本的な逐次エージェント
- **non_llm_sequential** - 非LLM逐次エージェント
- **adk_triaging_agent** - トリアージエージェント

### 5. MCP プロトコル統合系 (4エージェント)
- **mcp_sse_agent** - Server-Sent Events による MCP
- **mcp_stdio_notion_agent** - Notion との MCP STDIO 統合
- **mcp_stdio_server_agent** - 基本 MCP STDIO サーバー
- **mcp_streamablehttp_agent** - HTTP ストリーミング MCP

### 6. 高度機能デモ系 (8エージェント)
- **callbacks** - コールバックシステムの包括的デモ
- **memory** - セッション状態とメモリ管理
- **session_state_agent** - セッション間状態永続化
- **telemetry** - エージェント監視とテレメトリ
- **token_usage** - トークン消費追跡
- **human_in_loop** - Human-in-the-loop インタラクション
- **live_bidi_streaming_agent** - 双方向ストリーミング
- **toolbox_agent** - 外部ツールボックス統合

### 7. 特殊用途系 (6エージェント)
- **code_execution** - コード実行機能
- **generate_image** - 画像生成機能
- **rag_agent** - Retrieval-Augmented Generation
- **fields_output_schema** - 構造化出力スキーマ
- **fields_planner** - 構造化フィールドによるプランニング
- **langchain_structured_tool_agent** - LangChain 構造化ツール統合

### 8. 外部ライブラリ統合系 (2エージェント)
- **langchain_youtube_search_agent** - LangChain と YouTube 検索
- **langchain_structured_tool_agent** - LangChain 構造化ツール統合

## 標準ドキュメント構造

各エージェントの `TECHNICAL_DOCUMENTATION_ja.md` は以下の構造に従います：

```markdown
# [エージェント名] - 技術ドキュメント

## 1. エージェント概要
- 目的と用途
- 主要機能
- 対象ユースケース

## 2. アーキテクチャ解析
- 全体アーキテクチャ図 (テキスト)
- コンポーネント構成
- データフロー
- 依存関係

## 3. コード詳細解説
- メインコンポーネント解析
- ツール実装詳細
- 設定パラメータ
- 重要な実装パターン

## 4. 設定・環境構築
- 必要な環境変数
- 依存関係とインストール
- 認証設定
- 設定ファイル詳細

## 5. 使用パターンと拡張
- 基本的な使用例
- カスタマイズポイント
- 拡張方法
- 他のエージェントとの組み合わせ

## 6. トラブルシューティング
- よくあるエラーと解決法
- デバッグ方法
- パフォーマンス考慮事項

## 7. 開発者向けベストプラクティス
- このエージェントから学べるパターン
- 他のプロジェクトへの応用
- 推奨事項と注意点
```

## 実装順序

1. **基本/チュートリアル系** - ADK の基本パターンを理解
2. **Google サービス統合系** - 認証とサービス統合パターン
3. **外部API統合系** - 外部システム統合パターン
4. **マルチエージェント アーキテクチャ系** - 複雑なワークフロー
5. **MCP プロトコル統合系** - プロトコル統合パターン
6. **高度機能デモ系** - 高度な機能とコンセプト
7. **特殊用途系** - 特殊な用途と技術
8. **外部ライブラリ統合系** - サードパーティライブラリ統合

この順序により、基本から応用へと段階的に理解を深められる構成となります。