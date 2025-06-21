# hello_world_litellm - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`hello_world_litellm` エージェントは、ADK で LiteLLM を使用して複数の LLM プロバイダーに統一的にアクセスする方法を示すサンプル実装です。LiteLLM は OpenAI、Anthropic、Google、Azure OpenAI などの異なる LLM プロバイダーを統一されたインターフェースで利用できるライブラリです。

### 主要機能
- **統一 LLM インターフェース**: 複数プロバイダーへの統一アクセス
- **サイコロ振り機能**: 指定された面数のサイコロを振る
- **素数判定機能**: 数値のリストから素数を特定する
- **動的プロバイダー切り替え**: コメントアウトによる簡単な切り替え

### 対象ユースケース
- マルチプロバイダー LLM 戦略の実装
- プロバイダー間での性能・コスト比較
- フォールバック機能を持つロバストなシステム
- 統一インターフェースでの LLM 実験

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (質問/命令)
[hello_world_litellm_agent] 
    ↓ (LiteLLM 経由)
[LiteLLM ライブラリ]
    ↓ (プロバイダー選択)
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ OpenAI GPT-4o       │ Anthropic Claude    │ Google Gemini       │
│ (現在選択)          │ (コメントアウト)    │ (コメントアウト)    │
└─────────────────────┴─────────────────────┴─────────────────────┘
    ↓ (ツール呼び出し判断)
[カスタムツール群]
    ├── roll_die() - サイコロ振り
    └── check_prime() - 素数判定
```

### プロバイダー設定例
```python
# 利用可能なプロバイダー例（agent.py から）
# model=LiteLlm(model="gemini/gemini-2.5-pro-exp-03-25"),        # Google Gemini
# model=LiteLlm(model="vertex_ai/gemini-2.5-pro-exp-03-25"),    # Vertex AI Gemini  
# model=LiteLlm(model="vertex_ai/claude-3-5-haiku"),            # Vertex AI Claude
model=LiteLlm(model="openai/gpt-4o"),                          # OpenAI GPT-4o (アクティブ)
# model=LiteLlm(model="anthropic/claude-3-sonnet-20240229"),    # Anthropic Claude
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス + LiteLLM)
- **LLM プロキシ**: LiteLLM (`google.adk.models.lite_llm.LiteLlm`)
- **カスタムツール**: `roll_die`, `check_prime` (シンプル実装)
- **実行環境**: `Runner` + 個別サービス設定

### 依存関係
```python
# ADK コンポーネント
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm  # LiteLLM 統合
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
```

## 3. コード詳細解説

### 3.1 LiteLLM モデル設定

```python
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    model=LiteLlm(model="openai/gpt-4o"),
    # ...
)
```

**プロバイダー指定パターン:**
```python
# OpenAI 系
LiteLlm(model="openai/gpt-4o")
LiteLlm(model="openai/gpt-3.5-turbo")

# Anthropic 系  
LiteLlm(model="anthropic/claude-3-sonnet-20240229")
LiteLlm(model="anthropic/claude-3-5-haiku")

# Google 系
LiteLlm(model="gemini/gemini-2.5-pro-exp-03-25")
LiteLlm(model="vertex_ai/gemini-2.5-pro-exp-03-25")

# Vertex AI 経由の Anthropic
LiteLlm(model="vertex_ai/claude-3-5-haiku")
```

### 3.2 プロバイダー別の設定要件

#### OpenAI 設定
```bash
# 環境変数
OPENAI_API_KEY=your_openai_api_key
```

#### Anthropic 設定  
```bash
# 環境変数
ANTHROPIC_API_KEY=your_anthropic_api_key
```

#### Google/Vertex AI 設定
```bash
# Google AI Studio 使用時
GOOGLE_API_KEY=your_google_api_key

# Vertex AI 使用時
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# または
# gcloud auth application-default login
```

### 3.3 ツール実装

ツールの実装は他の hello_world バリエーションと同一：

```python
def roll_die(sides: int) -> int:
    """シンプルなサイコロ振り（状態管理なし）"""
    return random.randint(1, sides)

async def check_prime(nums: list[int]) -> str:
    """非同期素数判定"""
    # 実装は標準的な素数判定アルゴリズム
```

### 3.4 プロバイダー切り替えパターン

#### 開発・テスト時の切り替え
```python
def create_agent_with_provider(provider: str):
    provider_models = {
        "openai": "openai/gpt-4o",
        "anthropic": "anthropic/claude-3-sonnet-20240229", 
        "google": "gemini/gemini-2.5-pro-exp-03-25",
        "vertex_gemini": "vertex_ai/gemini-2.5-pro-exp-03-25",
        "vertex_claude": "vertex_ai/claude-3-5-haiku"
    }
    
    return Agent(
        model=LiteLlm(model=provider_models[provider]),
        name=f"agent_{provider}",
        tools=[roll_die, check_prime],
        # ...
    )
```

#### 環境変数による動的切り替え
```python
import os

def get_model_from_env():
    provider = os.getenv("LLM_PROVIDER", "openai")
    model_name = os.getenv("LLM_MODEL", "gpt-4o")
    return f"{provider}/{model_name}"

root_agent = Agent(
    model=LiteLlm(model=get_model_from_env()),
    # ...
)
```

## 4. 設定・環境構築

### 4.1 必要な環境変数

#### 基本設定（いずれか1つ以上）
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google AI Studio
GOOGLE_API_KEY=your_google_api_key

# Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

#### 追加設定（オプション）
```bash
# プロバイダー選択
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o

# LiteLLM ログレベル
LITELLM_LOG=DEBUG
```

### 4.2 依存関係とインストール

```bash
# 基本インストール
pip install google-adk[litellm]

# または個別インストール
pip install google-adk
pip install litellm

# 特定プロバイダーの追加依存関係
pip install openai      # OpenAI 用
pip install anthropic   # Anthropic 用
pip install google-generativeai  # Google AI Studio 用
```

### 4.3 プロバイダー別セットアップ

#### OpenAI セットアップ
```bash
# API キー取得: https://platform.openai.com/api-keys
export OPENAI_API_KEY=your_key
```

#### Anthropic セットアップ
```bash
# API キー取得: https://console.anthropic.com/
export ANTHROPIC_API_KEY=your_key
```

#### Google AI Studio セットアップ
```bash
# API キー取得: https://aistudio.google.com/app/apikey
export GOOGLE_API_KEY=your_key
```

#### Vertex AI セットアップ
```bash
# Google Cloud プロジェクト設定
gcloud config set project your-project-id
gcloud auth application-default login

# またはサービスアカウント使用
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 4.4 実行方法

```bash
# CLI での実行
adk run contributing/samples/hello_world_litellm

# Python スクリプトでの実行
cd contributing/samples/hello_world_litellm
python main.py

# Web UI での実行
adk web contributing/samples/hello_world_litellm
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### プロバイダー横断テスト
```python
# 複数プロバイダーでの同じタスク実行
providers = [
    "openai/gpt-4o",
    "anthropic/claude-3-sonnet-20240229",
    "gemini/gemini-2.5-pro-exp-03-25"
]

async def compare_providers(prompt: str):
    results = {}
    for provider in providers:
        agent = Agent(
            model=LiteLlm(model=provider),
            tools=[roll_die, check_prime],
            # ...
        )
        result = await run_agent(agent, prompt)
        results[provider] = result
    return results
```

### 5.2 フォールバック機能

#### プロバイダー障害時の自動切り替え
```python
class RobustLLMAgent:
    def __init__(self):
        self.providers = [
            "openai/gpt-4o",
            "anthropic/claude-3-sonnet-20240229", 
            "gemini/gemini-2.5-pro-exp-03-25"
        ]
        self.current_provider = 0
    
    async def run_with_fallback(self, prompt: str):
        for i in range(len(self.providers)):
            try:
                agent = Agent(
                    model=LiteLlm(model=self.providers[self.current_provider]),
                    tools=[roll_die, check_prime],
                    # ...
                )
                return await run_agent(agent, prompt)
            except Exception as e:
                print(f"Provider {self.providers[self.current_provider]} failed: {e}")
                self.current_provider = (self.current_provider + 1) % len(self.providers)
        
        raise Exception("All providers failed")
```

### 5.3 コスト最適化パターン

#### タスク複雑度に応じたプロバイダー選択
```python
def select_optimal_provider(task_complexity: str, budget_constraint: str):
    if task_complexity == "simple" and budget_constraint == "low":
        return "gemini/gemini-pro"  # 安価で高速
    elif task_complexity == "medium":
        return "openai/gpt-4o"      # バランス型
    elif task_complexity == "complex":
        return "anthropic/claude-3-opus"  # 高性能
    else:
        return "openai/gpt-3.5-turbo"  # デフォルト
```

#### 使用量監視
```python
class CostAwareLLMAgent:
    def __init__(self):
        self.usage_tracker = {
            "openai": {"requests": 0, "tokens": 0},
            "anthropic": {"requests": 0, "tokens": 0},
            "google": {"requests": 0, "tokens": 0}
        }
    
    def track_usage(self, provider: str, tokens: int):
        base_provider = provider.split('/')[0]
        self.usage_tracker[base_provider]["requests"] += 1
        self.usage_tracker[base_provider]["tokens"] += tokens
    
    def get_cheapest_provider(self):
        # コスト計算ロジック
        pass
```

### 5.4 A/B テスト実装

```python
import random

class ABTestLLMAgent:
    def __init__(self):
        self.test_groups = {
            "A": "openai/gpt-4o",
            "B": "anthropic/claude-3-sonnet-20240229"
        }
        self.results = {"A": [], "B": []}
    
    async def run_ab_test(self, prompt: str, user_id: str):
        # ユーザーをグループに割り当て
        group = "A" if hash(user_id) % 2 == 0 else "B"
        
        agent = Agent(
            model=LiteLlm(model=self.test_groups[group]),
            tools=[roll_die, check_prime],
            # ...
        )
        
        result = await run_agent(agent, prompt)
        self.results[group].append(result)
        return result, group
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "AuthenticationError" (プロバイダー別)
**原因**: API キーが未設定または無効
**解決法**: プロバイダー別の環境変数設定
```bash
# 使用プロバイダーに応じて設定
export OPENAI_API_KEY=your_key      # OpenAI 用
export ANTHROPIC_API_KEY=your_key   # Anthropic 用  
export GOOGLE_API_KEY=your_key      # Google 用
```

#### エラー: "ModuleNotFoundError: No module named 'litellm'"
**原因**: LiteLLM がインストールされていない
**解決法**: 適切なインストール
```bash
pip install google-adk[litellm]
# または
pip install litellm
```

#### エラー: "Model not supported"
**原因**: 無効なモデル名または未サポートプロバイダー
**解決法**: 有効なモデル名の確認
```python
# 有効なモデル名例
valid_models = [
    "openai/gpt-4o",
    "openai/gpt-3.5-turbo", 
    "anthropic/claude-3-sonnet-20240229",
    "gemini/gemini-pro"
]
```

### 6.2 デバッグ方法

#### LiteLLM ログの有効化
```python
import litellm
litellm.set_verbose = True  # 詳細ログを有効化

# 環境変数での設定
export LITELLM_LOG=DEBUG
```

#### プロバイダー接続テスト
```python
async def test_provider_connection(model_name: str):
    try:
        agent = Agent(
            model=LiteLlm(model=model_name),
            tools=[],
            instruction="Say hello"
        )
        result = await run_simple_test(agent)
        print(f"✅ {model_name}: Connection successful")
        return True
    except Exception as e:
        print(f"❌ {model_name}: {str(e)}")
        return False

# 全プロバイダーのテスト
models_to_test = [
    "openai/gpt-4o",
    "anthropic/claude-3-sonnet-20240229", 
    "gemini/gemini-pro"
]

for model in models_to_test:
    await test_provider_connection(model)
```

### 6.3 パフォーマンス最適化

#### レスポンス時間の比較
```python
import time

async def benchmark_providers(prompt: str):
    providers = [
        "openai/gpt-4o",
        "anthropic/claude-3-sonnet-20240229",
        "gemini/gemini-pro"
    ]
    
    results = {}
    for provider in providers:
        start_time = time.time()
        agent = Agent(model=LiteLlm(model=provider), tools=[])
        result = await run_agent(agent, prompt)
        end_time = time.time()
        
        results[provider] = {
            "response_time": end_time - start_time,
            "result": result
        }
    
    return results
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### 統一インターフェース設計
- 複数のバックエンドを統一 API で扱う
- プロバイダー固有の設定を抽象化
- 動的な実行時プロバイダー選択

#### 障害対応パターン
```python
# サーキットブレーカーパターン
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        
    def can_execute(self):
        if self.failure_count < self.failure_threshold:
            return True
            
        if time.time() - self.last_failure_time > self.timeout:
            self.failure_count = 0  # リセット
            return True
            
        return False
```

### 7.2 プロダクション環境での考慮事項

#### 設定管理
```python
# プロダクション設定例
class LLMConfig:
    def __init__(self):
        self.primary_provider = os.getenv("PRIMARY_LLM_PROVIDER", "openai/gpt-4o")
        self.fallback_providers = os.getenv(
            "FALLBACK_LLM_PROVIDERS", 
            "anthropic/claude-3-sonnet,gemini/gemini-pro"
        ).split(',')
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
```

#### 監視・アラート
```python
class LLMMonitor:
    def __init__(self):
        self.metrics = {
            "success_rate": {},
            "avg_response_time": {},
            "error_counts": {}
        }
    
    def log_request(self, provider: str, success: bool, response_time: float):
        # メトリクス記録
        if provider not in self.metrics["success_rate"]:
            self.metrics["success_rate"][provider] = []
        
        self.metrics["success_rate"][provider].append(success)
        
        # アラート条件チェック
        if not success:
            self.check_alert_conditions(provider)
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **プロバイダー多様化**: 単一プロバイダーへの依存回避
- **コスト監視**: 各プロバイダーの使用量とコストの追跡
- **性能ベンチマーク**: 定期的な性能・品質比較
- **設定の外部化**: 環境変数またはコンフィグファイルでの管理

#### 注意点
- **API 制限**: 各プロバイダーのレート制限の理解
- **データプライバシー**: 各プロバイダーのデータ処理ポリシー
- **コスト変動**: プロバイダー間の価格差と変動
- **機能差異**: プロバイダー固有の機能や制限

### 7.4 他のプロジェクトへの応用

#### マルチクラウド AI サービス
```python
class MultiCloudAIService:
    def __init__(self):
        self.llm_providers = {
            "text_generation": ["openai/gpt-4o", "anthropic/claude-3-sonnet"],
            "code_generation": ["openai/gpt-4o", "gemini/gemini-pro"],
            "translation": ["gemini/gemini-pro", "openai/gpt-4o"]
        }
    
    def get_best_provider(self, task_type: str):
        return self.llm_providers.get(task_type, ["openai/gpt-4o"])[0]
```

この hello_world_litellm エージェントは、マルチプロバイダー LLM 戦略の実装と、統一インターフェースによる柔軟性確保の重要性を学ぶのに最適な例です。特に企業環境でのベンダーロックイン回避とロバストなシステム構築に有用なパターンを提供します。