# hello_world_anthropic - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`hello_world_anthropic` エージェントは、ADK で Anthropic の Claude モデルを使用する方法を示すサンプル実装です。基本的な `hello_world` エージェントと同じ機能を提供しながら、異なる LLM プロバイダーとの統合パターンを学習するためのエージェントです。

### 主要機能
- **サイコロ振り機能**: 指定された面数のサイコロを振る
- **素数判定機能**: 数値のリストから素数を特定する
- **Anthropic Claude 統合**: Claude 3.5 Sonnet モデルの使用
- **並列ツール実行**: 複数のツールを一度のリクエストで実行可能

### 対象ユースケース
- Anthropic Claude モデルの ADK 統合学習
- 複数 LLM プロバイダー対応の理解
- 外部 LLM サービスとの統合パターン
- プロバイダー固有の設定方法の学習

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (質問/命令)
[hello_world_agent] 
    ↓ (Claude API 経由)
[Anthropic Claude 3.5 Sonnet]
    ↓ (ツール呼び出し判断)
[カスタムツール群]
    ├── roll_die() - サイコロ振り (シンプル実装)
    └── check_prime() - 素数判定
    ↓ (結果)
[Claude による解釈・応答]
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス + Claude モデル)
- **LLM プロバイダー**: Anthropic Claude (`google.adk.models.anthropic_llm.Claude`)
- **カスタムツール**: `roll_die`, `check_prime` (状態管理なし)
- **実行環境**: `Runner` + 個別サービス設定

### Google モデルとの違い
| 項目 | hello_world (Google) | hello_world_anthropic (Anthropic) |
|------|---------------------|-----------------------------------|
| モデル指定 | `model='gemini-2.0-flash'` | `model=Claude(model="claude-3-5-sonnet-v2@20241022")` |
| 状態管理 | `ToolContext` パラメータ | 状態管理なし |
| Runner 設定 | `InMemoryRunner` | `Runner` + 個別サービス |
| 安全設定 | `SafetySetting` 設定 | 設定なし |

### 依存関係
```python
# 標準ライブラリ
import random  # サイコロ振り用
import asyncio  # 非同期実行用

# ADK コンポーネント
from google.adk import Agent
from google.adk.models.anthropic_llm import Claude  # Anthropic 統合
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
```

## 3. コード詳細解説

### 3.1 Anthropic Claude モデル設定

```python
from google.adk.models.anthropic_llm import Claude

root_agent = Agent(
    model=Claude(model="claude-3-5-sonnet-v2@20241022"),
    # ...
)
```

**重要な実装ポイント:**
- **明示的なモデルクラス**: `Claude` クラスをインスタンス化
- **具体的なモデルバージョン**: 日付付きバージョン指定
- **プロバイダー固有の設定**: Anthropic 特有の設定オプション

### 3.2 シンプルなツール実装

#### roll_die ツール (状態管理なし)
```python
def roll_die(sides: int) -> int:
  """Roll a die and return the rolled result.

  Args:
    sides: The integer number of sides the die has.

  Returns:
    An integer of the result of rolling the die.
  """
  return random.randint(1, sides)
```

**Google 版との違い:**
- `ToolContext` パラメータが不要
- 状態管理機能なし
- よりシンプルな実装

#### check_prime ツール
```python
async def check_prime(nums: list[int]) -> str:
  """Check if a given list of numbers are prime."""
  # 実装は hello_world と同じ
  primes = set()
  for number in nums:
    # 素数判定ロジック...
  return result_string
```

**特徴:**
- 非同期実装を維持
- アルゴリズムは Google 版と同一
- 戻り値の形式も統一

### 3.3 実行環境設定 (main.py)

#### サービス設定
```python
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = Runner(
    app_name=app_name,
    agent=agent.root_agent,
    artifact_service=artifact_service,
    session_service=session_service,
)
```

**Google 版との違い:**
- **個別サービス作成**: 各サービスを明示的にインスタンス化
- **Runner クラス**: `InMemoryRunner` ではなく基本 `Runner`
- **詳細制御**: より細かいサービス制御が可能

#### 実行パターン
```python
await run_prompt(session_11, 'Hi, introduce yourself.')
await run_prompt(
    session_11,
    'Run the following request 10 times: roll a die with 100 sides and check'
    ' if it is prime',
)
```

**特徴:**
- より複雑なタスクの実行
- 反復処理の指示
- Claude の推論能力を活用

## 4. 設定・環境構築

### 4.1 必要な環境変数
```bash
# .env ファイルまたは環境変数
# Anthropic API の設定
ANTHROPIC_API_KEY=your_anthropic_api_key

# または
CLAUDE_API_KEY=your_anthropic_api_key
```

### 4.2 依存関係とインストール
```bash
# ADK with Anthropic 支援
pip install google-adk[anthropic]

# または個別インストール
pip install google-adk
pip install anthropic  # Anthropic SDK
```

### 4.3 API キーの取得
1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウント作成またはログイン
3. API キーを生成
4. 環境変数に設定

### 4.4 実行方法
```bash
# CLI での実行
adk run contributing/samples/hello_world_anthropic

# Python スクリプトでの実行
cd contributing/samples/hello_world_anthropic
python main.py

# Web UI での実行
adk web contributing/samples/hello_world_anthropic
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### Claude の自己紹介
```
ユーザー: "Hi, introduce yourself."
Claude: "Hello! I'm Claude, an AI assistant created by Anthropic. I can help you with dice rolling and prime number checking using the tools I have available."
```

#### 複雑なタスク実行
```
ユーザー: "Run the following request 10 times: roll a die with 100 sides and check if it is prime"
Claude: [10回の roll_die と check_prime の組み合わせを実行]
"I've completed 10 dice rolls and prime checks. Here are the results: ..."
```

### 5.2 他の Claude モデルの使用

#### Claude 3 Haiku (高速・安価)
```python
root_agent = Agent(
    model=Claude(model="claude-3-haiku@20240307"),
    # ...
)
```

#### Claude 3 Opus (最高性能)
```python
root_agent = Agent(
    model=Claude(model="claude-3-opus@20240229"),
    # ...
)
```

### 5.3 プロバイダー比較エージェント
```python
# 複数プロバイダー対応エージェント
def create_multi_provider_agent(provider: str):
    if provider == "google":
        model = "gemini-2.0-flash"
    elif provider == "anthropic":
        model = Claude(model="claude-3-5-sonnet-v2@20241022")
    elif provider == "openai":
        model = "gpt-4"
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    return Agent(
        model=model,
        name=f"{provider}_agent",
        tools=[roll_die, check_prime],
        # ...
    )

# 使用例
google_agent = create_multi_provider_agent("google")
anthropic_agent = create_multi_provider_agent("anthropic")
```

### 5.4 Claude 固有の機能活用
```python
# Claude の詳細な推論能力を活用
root_agent = Agent(
    model=Claude(model="claude-3-5-sonnet-v2@20241022"),
    instruction="""
    You are a mathematical assistant with access to dice rolling and prime checking tools.
    
    When performing calculations:
    1. Show your reasoning step by step
    2. Explain the mathematical concepts involved
    3. Use the tools to verify your calculations
    4. Provide educational context when appropriate
    
    Claude's strength in detailed explanation should be leveraged.
    """,
    tools=[roll_die, check_prime],
)
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "AuthenticationError: Invalid API key"
**原因**: Anthropic API キーが設定されていない
**解決法**: 環境変数の確認と設定
```bash
# 環境変数の確認
echo $ANTHROPIC_API_KEY

# .env ファイルでの設定
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

#### エラー: "ModuleNotFoundError: No module named 'anthropic'"
**原因**: Anthropic SDK がインストールされていない
**解決法**: 適切なインストール
```bash
pip install google-adk[anthropic]
# または
pip install anthropic
```

#### エラー: "RateLimitError: Rate limit exceeded"
**原因**: API 使用量制限に達した
**解決法**: レート制限の管理
```python
import asyncio

async def rate_limited_call():
    # リクエスト間隔を調整
    await asyncio.sleep(1)  # 1秒待機
    return await runner.run_async(...)
```

### 6.2 パフォーマンス最適化

#### モデル選択の最適化
```python
# タスク複雑度に応じたモデル選択
def select_claude_model(task_complexity: str):
    if task_complexity == "simple":
        return Claude(model="claude-3-haiku@20240307")  # 高速・安価
    elif task_complexity == "medium":
        return Claude(model="claude-3-5-sonnet-v2@20241022")  # バランス
    else:
        return Claude(model="claude-3-opus@20240229")  # 最高性能
```

#### バッチ処理の実装
```python
async def batch_process_requests(requests: list[str]):
    tasks = []
    for request in requests:
        task = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role='user', 
                parts=[types.Part.from_text(text=request)]
            ),
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 6.3 デバッグとモニタリング

#### API 使用量の追跡
```python
import logging

class ClaudeUsageTracker:
    def __init__(self):
        self.request_count = 0
        self.token_usage = 0
    
    def log_request(self, request_data):
        self.request_count += 1
        logging.info(f"Claude API request #{self.request_count}")
        
    def log_response(self, response_data):
        if hasattr(response_data, 'usage'):
            self.token_usage += response_data.usage.total_tokens
            logging.info(f"Total tokens used: {self.token_usage}")
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### マルチプロバイダー対応
- 統一されたインターフェースでの複数 LLM 対応
- プロバイダー固有の設定パターン
- API キー管理のベストプラクティス

#### サービス構成の柔軟性
```python
# 環境に応じたサービス選択
def create_services(environment: str):
    if environment == "development":
        return InMemorySessionService(), InMemoryArtifactService()
    elif environment == "production":
        return DatabaseSessionService(), CloudArtifactService()
    else:
        raise ValueError(f"Unknown environment: {environment}")
```

### 7.2 プロバイダー選択の指針

#### Google Gemini vs Anthropic Claude
| 項目 | Google Gemini | Anthropic Claude |
|------|---------------|------------------|
| **強み** | 統合性、速度、多言語 | 推論力、詳細説明、安全性 |
| **適用場面** | 検索、分析、翻訳 | 文章作成、教育、推論 |
| **コスト** | 比較的安価 | 高品質だが高コスト |
| **レスポンス** | 高速 | やや時間がかかる |

#### 選択基準
```python
def select_provider(task_type: str, budget: str, response_time_requirement: str):
    if task_type == "simple_qa" and response_time_requirement == "fast":
        return "google"
    elif task_type == "complex_reasoning" and budget == "flexible":
        return "anthropic"
    elif task_type == "creative_writing":
        return "anthropic"
    else:
        return "google"  # デフォルト
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **環境変数管理**: API キーの安全な管理
- **エラーハンドリング**: プロバイダー固有のエラーへの対応
- **コスト監視**: API 使用量の定期的な確認
- **モデル更新**: 新しいモデルバージョンへの対応

#### 注意点
- **API 制限**: レート制限とクォータの理解
- **データプライバシー**: 外部サービスへの情報送信
- **依存関係**: 外部サービスの可用性への依存
- **コスト管理**: 予期しない高額な API 使用料

### 7.4 他のプロジェクトへの応用

#### マルチモデル比較システム
```python
class MultiModelComparison:
    def __init__(self):
        self.models = {
            "google": Agent(model="gemini-2.0-flash", tools=tools),
            "anthropic": Agent(model=Claude(model="claude-3-5-sonnet-v2@20241022"), tools=tools),
            "openai": Agent(model="gpt-4", tools=tools)
        }
    
    async def compare_responses(self, prompt: str):
        results = {}
        for provider, agent in self.models.items():
            results[provider] = await self.run_agent(agent, prompt)
        return results
```

この hello_world_anthropic エージェントは、ADK における複数 LLM プロバイダー対応の基本パターンを学ぶのに適した例です。特に Anthropic Claude の統合方法と、プロバイダー固有の設定パターンを理解するのに有用です。