# artifact_save_text - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`artifact_save_text` エージェントは、ADK のアーティファクト保存機能を学習するための最もシンプルなサンプル実装です。ユーザーのクエリをテキストファイルとしてアーティファクトシステムに保存し、データの永続化とファイル管理の基本パターンを示します。

### 主要機能
- **クエリログ機能**: ユーザーの入力を自動的にログとして保存
- **アーティファクト管理**: ADK のアーティファクトシステムとの統合
- **テキストファイル生成**: UTF-8 エンコードでのテキストファイル作成
- **自動応答**: 保存完了の確認メッセージ

### 対象ユースケース
- アーティファクトシステムの基本理解
- ファイル保存・管理機能の学習
- データ永続化パターンの実装
- ログ機能の基本実装

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザークエリ] 
    ↓ (入力)
[log_agent] 
    ↓ (自動実行)
[log_query ツール]
    ↓ (エンコード・保存)
[アーティファクトシステム]
    └── 'query' ファイル (text/plain)
    ↓ (応答)
[確認メッセージ] → "kk, I've logged."
```

### データフロー
1. ユーザーが任意のクエリを入力
2. エージェントが自動的に `log_query` ツールを呼び出し
3. クエリテキストが UTF-8 でエンコード
4. `types.Blob` オブジェクトとしてラップ
5. アーティファクトシステムに 'query' という名前で保存
6. 保存完了を確認メッセージで通知

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス)
- **ログツール**: `log_query` - テキスト保存専用
- **アーティファクトシステム**: ADK 組み込みの永続化機能
- **安全設定**: コンテンツフィルタの調整

### 依存関係
```python
# ADK コンポーネント
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
```

## 3. コード詳細解説

### 3.1 アーティファクト保存ツール

```python
async def log_query(tool_context: ToolContext, query: str):
  """Saves the provided query string as a 'text/plain' artifact named 'query'."""
  query_bytes = query.encode('utf-8')
  artifact_part = types.Part(
      inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
  )
  await tool_context.save_artifact('query', artifact_part)
```

**重要な実装ポイント:**

#### 1. 非同期実装
- `async def` - アーティファクト保存は非同期操作
- `await tool_context.save_artifact()` - 非同期でファイル保存

#### 2. エンコード処理
```python
query_bytes = query.encode('utf-8')
```
- 文字列をバイト列に変換
- UTF-8 エンコードで国際化対応

#### 3. MIME タイプ指定
```python
mime_type='text/plain'
```
- ファイルタイプを明示的に指定
- ブラウザ等での適切な表示を保証

#### 4. Blob オブジェクト作成
```python
artifact_part = types.Part(
    inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
)
```
- `types.Blob`: バイナリデータのラッパー
- `types.Part`: マルチパートデータ構造
- `inline_data`: データを直接埋め込み

#### 5. アーティファクト保存
```python
await tool_context.save_artifact('query', artifact_part)
```
- `'query'`: アーティファクト名（ファイル名）
- 既存ファイルは上書きされる

### 3.2 エージェント設定

```python
root_agent = Agent(
    model='gemini-2.0-flash',
    name='log_agent',
    description='Log user query.',
    instruction="""Always log the user query and reploy "kk, I've logged."
    """,
    tools=[log_query],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
```

**設計の特徴:**

#### シンプルな指示
- 常にユーザークエリをログ
- 固定の応答メッセージ
- 最小限の機能に特化

#### 安全設定
- 危険コンテンツフィルタを無効化
- ログ機能での誤検出を防止

## 4. 設定・環境構築

### 4.1 必要な環境変数
```bash
# .env ファイルまたは環境変数
GOOGLE_API_KEY=your_google_api_key
```

### 4.2 依存関係とインストール
```bash
# 基本依存関係は ADK に含まれる
pip install google-adk
```

### 4.3 実行方法
```bash
# CLI での実行
adk run contributing/samples/artifact_save_text

# Web UI での実行
adk web contributing/samples/artifact_save_text
```

### 4.4 アーティファクトの確認
```bash
# CLI でのアーティファクト一覧表示
adk artifacts list

# 特定セッションのアーティファクト確認
adk artifacts list --session-id <session_id>
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### クエリのログ
```
ユーザー: "Hello, how are you?"
エージェント: [log_query ツールを自動実行] "kk, I've logged."

結果: 'query' ファイルに "Hello, how are you?" が保存される
```

#### 長いテキストのログ
```
ユーザー: "Please write a detailed analysis of the current economic situation..."
エージェント: [log_query ツールを自動実行] "kk, I've logged."

結果: 長いテキストも完全にログファイルに保存される
```

### 5.2 拡張パターン

#### 複数ファイル形式の保存
```python
async def log_query_enhanced(tool_context: ToolContext, query: str):
    """Enhanced logging with multiple formats"""
    import json
    from datetime import datetime
    
    # テキスト形式で保存
    query_bytes = query.encode('utf-8')
    text_part = types.Part(
        inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
    )
    await tool_context.save_artifact('query.txt', text_part)
    
    # JSON形式で保存（メタデータ付き）
    query_data = {
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'length': len(query),
        'encoding': 'utf-8'
    }
    json_bytes = json.dumps(query_data, ensure_ascii=False, indent=2).encode('utf-8')
    json_part = types.Part(
        inline_data=types.Blob(mime_type='application/json', data=json_bytes)
    )
    await tool_context.save_artifact('query.json', json_part)
```

#### ファイル名の動的生成
```python
async def log_query_timestamped(tool_context: ToolContext, query: str):
    """Save query with timestamp-based filename"""
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'query_{timestamp}.txt'
    
    query_bytes = query.encode('utf-8')
    artifact_part = types.Part(
        inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
    )
    await tool_context.save_artifact(filename, artifact_part)
```

#### 構造化ログの実装
```python
async def structured_log(tool_context: ToolContext, query: str, log_level: str = "INFO"):
    """Structured logging with log levels"""
    import json
    from datetime import datetime
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': log_level,
        'message': query,
        'source': 'user_input',
        'session_id': getattr(tool_context, 'session_id', 'unknown')
    }
    
    log_bytes = json.dumps(log_entry, ensure_ascii=False, indent=2).encode('utf-8')
    log_part = types.Part(
        inline_data=types.Blob(mime_type='application/json', data=log_bytes)
    )
    
    # ログレベル別のファイルに保存
    filename = f'log_{log_level.lower()}.jsonl'
    await tool_context.save_artifact(filename, log_part)
```

### 5.3 バイナリファイルの保存
```python
async def save_binary_data(tool_context: ToolContext, data: bytes, filename: str, mime_type: str):
    """Save binary data as artifact"""
    artifact_part = types.Part(
        inline_data=types.Blob(mime_type=mime_type, data=data)
    )
    await tool_context.save_artifact(filename, artifact_part)

# 画像保存の例
async def save_image(tool_context: ToolContext, image_bytes: bytes):
    await save_binary_data(tool_context, image_bytes, 'image.png', 'image/png')

# PDF保存の例  
async def save_pdf(tool_context: ToolContext, pdf_bytes: bytes):
    await save_binary_data(tool_context, pdf_bytes, 'document.pdf', 'application/pdf')
```

### 5.4 アーティファクト管理エージェント
```python
async def list_artifacts(tool_context: ToolContext) -> str:
    """List all saved artifacts"""
    # 注意: この機能は現在のADKでは直接サポートされていない可能性があります
    # 実装は環境に依存します
    return "Artifact listing functionality needs to be implemented"

async def delete_artifact(tool_context: ToolContext, filename: str):
    """Delete a specific artifact"""
    # 注意: 削除機能の実装も環境依存です
    pass

file_manager_agent = Agent(
    model='gemini-2.0-flash',
    name='file_manager',
    description='Manage saved artifacts',
    tools=[log_query, list_artifacts, delete_artifact],
    # ...
)
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "AttributeError: 'ToolContext' object has no attribute 'save_artifact'"
**原因**: ADK バージョンが古いまたはツールコンテキストが正しく初期化されていない
**解決法**: ADK の更新と正しい実行環境の確認
```bash
pip install --upgrade google-adk
```

#### エラー: "UnicodeEncodeError"
**原因**: 特殊文字のエンコード問題
**解決法**: 適切なエラーハンドリング
```python
async def safe_log_query(tool_context: ToolContext, query: str):
    try:
        query_bytes = query.encode('utf-8')
    except UnicodeEncodeError as e:
        # フォールバック: エラー文字を置換
        query_bytes = query.encode('utf-8', errors='replace')
        
    # 残りの処理...
```

#### エラー: "File size too large"
**原因**: アーティファクトサイズ制限
**解決法**: サイズ制限の確認と分割保存
```python
async def log_large_query(tool_context: ToolContext, query: str, max_size: int = 1024*1024):
    """Large text handling with chunking"""
    query_bytes = query.encode('utf-8')
    
    if len(query_bytes) > max_size:
        # チャンク分割
        chunks = [query_bytes[i:i+max_size] for i in range(0, len(query_bytes), max_size)]
        
        for i, chunk in enumerate(chunks):
            chunk_part = types.Part(
                inline_data=types.Blob(mime_type='text/plain', data=chunk)
            )
            await tool_context.save_artifact(f'query_chunk_{i+1}.txt', chunk_part)
    else:
        # 通常の保存
        artifact_part = types.Part(
            inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
        )
        await tool_context.save_artifact('query.txt', artifact_part)
```

### 6.2 デバッグ方法

#### ログ出力の追加
```python
import logging

async def debug_log_query(tool_context: ToolContext, query: str):
    """Debug version with logging"""
    logging.info(f"Starting to log query: {query[:50]}...")
    
    try:
        query_bytes = query.encode('utf-8')
        logging.info(f"Encoded query size: {len(query_bytes)} bytes")
        
        artifact_part = types.Part(
            inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
        )
        
        await tool_context.save_artifact('query', artifact_part)
        logging.info("Successfully saved artifact")
        
    except Exception as e:
        logging.error(f"Failed to save artifact: {str(e)}")
        raise
```

### 6.3 パフォーマンス考慮事項

- **ファイルサイズ**: 大きなテキストの保存時間
- **エンコード処理**: 非 ASCII 文字のオーバーヘッド
- **アーティファクトストレージ**: ストレージ容量の管理

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### アーティファクト管理の基本
- `ToolContext.save_artifact()` の使用方法
- MIME タイプの適切な指定
- バイナリデータの扱い方

#### ファイル処理パターン
- UTF-8 エンコードの重要性
- `types.Blob` と `types.Part` の使い分け
- 非同期処理での I/O 操作

### 7.2 他のプロジェクトへの応用

#### ドキュメント生成エージェント
```python
async def generate_report(tool_context: ToolContext, data: dict):
    """Generate and save report"""
    import json
    
    # HTMLレポート生成
    html_content = f"""
    <html>
    <head><title>Report</title></head>
    <body>
        <h1>Data Report</h1>
        <pre>{json.dumps(data, indent=2)}</pre>
    </body>
    </html>
    """
    
    html_bytes = html_content.encode('utf-8')
    html_part = types.Part(
        inline_data=types.Blob(mime_type='text/html', data=html_bytes)
    )
    await tool_context.save_artifact('report.html', html_part)
```

#### 設定ファイル管理
```python
async def save_config(tool_context: ToolContext, config: dict):
    """Save configuration as YAML"""
    import yaml
    
    yaml_content = yaml.dump(config, default_flow_style=False, allow_unicode=True)
    yaml_bytes = yaml_content.encode('utf-8')
    yaml_part = types.Part(
        inline_data=types.Blob(mime_type='application/x-yaml', data=yaml_bytes)
    )
    await tool_context.save_artifact('config.yaml', yaml_part)
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **適切なMIMEタイプ**: ファイル内容に応じた正確な指定
- **エラーハンドリング**: エンコードエラーやサイズ制限への対応
- **ファイル命名**: 意味のある、衝突しないファイル名
- **メタデータ**: 作成日時や用途をファイルに含める

#### 注意点
- **ファイルサイズ**: アーティファクトシステムの制限
- **文字エンコード**: 国際化対応
- **ファイル上書き**: 同名ファイルの扱い
- **セキュリティ**: 機密情報の保存に注意

この artifact_save_text エージェントは、ADK におけるファイル保存とアーティファクト管理の基本パターンを理解するのに最適なサンプルです。シンプルな実装ながら、データ永続化の重要な概念を学ぶことができます。