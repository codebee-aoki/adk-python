# hello_world_ollama - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`hello_world_ollama` エージェントは、ADK で Ollama（ローカル LLM 実行環境）を使用する方法を示すサンプル実装です。LiteLLM を通じて Ollama で稼働するローカル LLM モデル（Mistral Small 3.1）を利用し、プライバシーと自律性を重視したAIエージェント開発パターンを提供します。

### 主要機能
- **ローカル LLM 統合**: Ollama による完全にローカルでの LLM 実行
- **サイコロ振り機能**: 指定された面数のサイコロを振る
- **素数判定機能**: 数値のリストから素数を特定する
- **プライバシー重視**: データが外部に送信されない環境

### 対象ユースケース
- ローカル LLM 環境での AI エージェント開発
- データプライバシーが重要なアプリケーション
- インターネット接続が制限された環境
- 機密情報を扱うシステム

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (質問/命令)
[dice_roll_agent] 
    ↓ (LiteLLM 経由)
[LiteLLM]
    ↓ (ローカル通信)
[Ollama サーバー] (localhost:11434)
    ↓ (モデル実行)
[Mistral Small 3.1] (ローカルモデル)
    ↓ (ツール呼び出し判断)
[カスタムツール群]
    ├── roll_die() - サイコロ振り
    └── check_prime() - 素数判定
```

### ローカル実行の利点
- **データプライバシー**: すべての処理がローカル環境で完結
- **レイテンシー**: ネットワーク遅延なし
- **コスト**: API 使用料金なし
- **可用性**: インターネット接続不要

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス + LiteLLM)
- **LLM プロキシ**: LiteLLM + Ollama 統合
- **ローカルモデル**: Mistral Small 3.1
- **カスタムツール**: `roll_die`, `check_prime` (シンプル実装)

### 依存関係
```python
# ADK コンポーネント
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# 外部依存関係
# - Ollama サーバー (localhost:11434)
# - Mistral Small 3.1 モデル
```

## 3. コード詳細解説

### 3.1 Ollama + LiteLLM 設定

```python
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    # ...
)
```

**重要な設定ポイント:**

#### モデル指定パターン
```python
# Ollama モデルの指定形式
LiteLlm(model="ollama_chat/model_name")

# 利用可能なモデル例
LiteLlm(model="ollama_chat/mistral-small3.1")   # Mistral Small 3.1
LiteLlm(model="ollama_chat/llama3.1")           # Llama 3.1
LiteLlm(model="ollama_chat/codellama")          # Code Llama
LiteLlm(model="ollama_chat/gemma")              # Gemma
```

#### LiteLLM - Ollama 統合
- `ollama_chat/` プレフィックスで Ollama モデルを指定
- ローカルの Ollama サーバー（デフォルト: `localhost:11434`）に接続
- HTTP API 経由でモデルと通信

### 3.2 ツール実装

ツールの実装は他の hello_world バリエーションとほぼ同一：

```python
def roll_die(sides: int) -> int:
    """Roll a die and return the rolled result."""
    return random.randint(1, sides)

def check_prime(numbers: list[int]) -> str:
    """Check if a given list of numbers are prime."""
    # 標準的な素数判定アルゴリズム
    # 注意: 同期関数として実装（非同期ではない）
```

**他バリエーションとの違い:**
- `check_prime` が同期関数（`async` なし）
- パラメータ名が `numbers` （`nums` ではない）
- その他のロジックは同一

### 3.3 エージェント設定

```python
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_roll_agent",
    description=(
        "hello world agent that can roll a dice of any number of sides and"
        " check prime numbers."
    ),
    instruction="""
      # 詳細な指示（他のバリエーションと同じ）
    """,
    tools=[roll_die, check_prime],
)
```

**設計の特徴:**
- シンプルな設定（安全設定なし）
- Ollama 特有の設定は不要
- ローカル実行のためのAPI キー不要

## 4. 設定・環境構築

### 4.1 Ollama サーバーのセットアップ

#### Ollama のインストール
```bash
# macOS (Homebrew)
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# https://ollama.ai からインストーラーをダウンロード
```

#### Ollama サーバーの起動
```bash
# サーバー起動
ollama serve

# バックグラウンド実行
nohup ollama serve &
```

#### Mistral Small 3.1 モデルのダウンロード
```bash
# モデルの取得
ollama pull mistral-small:3.1

# または短縮名
ollama pull mistral-small3.1

# 利用可能モデルの確認
ollama list
```

### 4.2 代替モデルのセットアップ

#### Llama 3.1 の使用
```bash
# モデルダウンロード
ollama pull llama3.1

# エージェント設定の変更
model=LiteLlm(model="ollama_chat/llama3.1")
```

#### Code Llama の使用
```bash
# コード生成特化モデル
ollama pull codellama

# エージェント設定
model=LiteLlm(model="ollama_chat/codellama")
```

### 4.3 依存関係とインストール

```bash
# 基本依存関係
pip install google-adk[litellm]

# または個別インストール
pip install google-adk
pip install litellm

# Ollama Python クライアント（オプション）
pip install ollama
```

### 4.4 環境変数（オプション）

```bash
# Ollama サーバーの場所（デフォルト: localhost:11434）
export OLLAMA_HOST=localhost:11434

# LiteLLM 設定
export LITELLM_LOG=INFO
```

### 4.5 実行方法

```bash
# 1. Ollama サーバーを起動
ollama serve

# 2. 必要なモデルをダウンロード
ollama pull mistral-small3.1

# 3. エージェントを実行
adk run contributing/samples/hello_world_ollama

# または Python スクリプト実行
cd contributing/samples/hello_world_ollama
python main.py

# Web UI での実行
adk web contributing/samples/hello_world_ollama
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### ローカル環境でのサイコロ振り
```
ユーザー: "Roll a 20-sided die"
Mistral Small 3.1: [roll_die ツールを呼び出し] "I rolled a 15 for you!"
```

#### オフライン環境での素数チェック
```
ユーザー: "Check if 17, 18, and 19 are prime numbers"
Mistral Small 3.1: [check_prime ツールを呼び出し] "17 and 19 are prime numbers."
```

### 5.2 モデル比較とベンチマーク

#### 複数モデルでの性能比較
```python
def create_ollama_agent(model_name: str):
    return Agent(
        model=LiteLlm(model=f"ollama_chat/{model_name}"),
        name=f"agent_{model_name}",
        tools=[roll_die, check_prime],
        # ...
    )

# 異なるモデルでテスト
models = ["mistral-small3.1", "llama3.1", "codellama", "gemma"]
agents = {name: create_ollama_agent(name) for name in models}

async def compare_models(prompt: str):
    results = {}
    for model_name, agent in agents.items():
        start_time = time.time()
        result = await run_agent(agent, prompt)
        end_time = time.time()
        
        results[model_name] = {
            "result": result,
            "response_time": end_time - start_time
        }
    return results
```

### 5.3 カスタムモデルの使用

#### Modelfile での独自モデル作成
```bash
# Modelfile 作成
cat > Modelfile << 'EOF'
FROM mistral-small3.1

# カスタムパラメータ
PARAMETER temperature 0.8
PARAMETER top_p 0.9
PARAMETER top_k 40

# システムプロンプト
SYSTEM You are a helpful assistant specialized in mathematics and probability.
EOF

# カスタムモデル作成
ollama create my-custom-model -f Modelfile

# エージェントで使用
model=LiteLlm(model="ollama_chat/my-custom-model")
```

### 5.4 リソース管理

#### メモリ使用量の監視
```python
import psutil

class ResourceMonitor:
    def __init__(self):
        self.initial_memory = psutil.virtual_memory().used
    
    def get_memory_usage(self):
        current_memory = psutil.virtual_memory().used
        return current_memory - self.initial_memory
    
    def monitor_ollama_process(self):
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            if 'ollama' in proc.info['name'].lower():
                return proc.info['memory_info'].rss
        return None

# 使用例
monitor = ResourceMonitor()
memory_before = monitor.get_memory_usage()
result = await run_agent(agent, prompt)
memory_after = monitor.get_memory_usage()
print(f"Memory used: {memory_after - memory_before} bytes")
```

### 5.5 パフォーマンス最適化

#### モデル事前ロード
```bash
# モデルを事前にロードしてウォームアップ
ollama run mistral-small3.1 "Hello"

# 継続実行でメモリに保持
ollama run mistral-small3.1 --keep-alive 60m
```

#### 並列処理
```python
async def parallel_ollama_requests(prompts: list[str]):
    agents = [create_ollama_agent("mistral-small3.1") for _ in prompts]
    
    tasks = []
    for agent, prompt in zip(agents, prompts):
        task = run_agent(agent, prompt)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "ConnectionError: Could not connect to Ollama"
**原因**: Ollama サーバーが起動していない
**解決法**: サーバーの起動確認
```bash
# サーバー状態確認
ps aux | grep ollama

# サーバー起動
ollama serve

# 接続テスト
curl http://localhost:11434/api/tags
```

#### エラー: "Model not found: mistral-small3.1"
**原因**: 指定モデルがダウンロードされていない
**解決法**: モデルのダウンロード
```bash
# 利用可能モデル確認
ollama list

# モデルダウンロード
ollama pull mistral-small3.1

# モデル削除（必要な場合）
ollama rm mistral-small3.1
```

#### エラー: "Out of memory"
**原因**: システムメモリ不足
**解決法**: リソース最適化
```bash
# 軽量モデルの使用
ollama pull gemma:2b  # 2Bパラメータモデル

# メモリ使用量確認
ollama ps

# 不要なモデルの停止
ollama stop mistral-small3.1
```

### 6.2 パフォーマンスチューニング

#### GPU 使用の確認
```bash
# GPU 使用状況確認
nvidia-smi  # NVIDIA GPU

# Metal 使用確認 (macOS)
ollama run mistral-small3.1 --verbose
```

#### モデルパラメータ調整
```bash
# 高速だが低品質
ollama run mistral-small3.1 --temperature 0.1 --top-p 0.5

# 高品質だが低速
ollama run mistral-small3.1 --temperature 0.8 --top-p 0.9
```

### 6.3 デバッグ方法

#### 詳細ログの有効化
```bash
# Ollama ログレベル設定
export OLLAMA_DEBUG=1

# LiteLLM ログ
export LITELLM_LOG=DEBUG

# サーバー再起動
ollama serve
```

#### API 直接テスト
```bash
# 直接 API テスト
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small3.1",
    "prompt": "Hello world",
    "stream": false
  }'
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### ローカル LLM 統合
- Ollama サーバーとの適切な連携
- モデル管理とリソース制御
- オフライン環境での AI エージェント運用

#### プライバシー重視設計
```python
# プライバシー重視のエージェント設計例
class PrivacyAwareAgent:
    def __init__(self):
        self.local_only = True
        self.data_retention = False
        
    def validate_privacy(self, data):
        # 機密データのチェック
        if self.contains_sensitive_info(data):
            raise ValueError("Sensitive data detected")
        return True
    
    def contains_sensitive_info(self, data):
        # PII検出ロジック
        sensitive_patterns = [
            r'\d{3}-\d{2}-\d{4}',  # SSN
            r'\d{4}-\d{4}-\d{4}-\d{4}',  # クレジットカード
        ]
        # 検出実装...
        return False
```

### 7.2 プロダクション環境での考慮事項

#### リソース管理
```python
class OllamaResourceManager:
    def __init__(self):
        self.max_memory_usage = 8 * 1024 * 1024 * 1024  # 8GB
        self.model_cache_timeout = 3600  # 1時間
    
    def check_system_resources(self):
        memory = psutil.virtual_memory()
        if memory.available < self.max_memory_usage:
            raise ResourceError("Insufficient memory")
    
    def cleanup_unused_models(self):
        # 未使用モデルのクリーンアップ
        pass
```

#### 高可用性設計
```python
class HighAvailabilityOllama:
    def __init__(self):
        self.ollama_instances = [
            "localhost:11434",
            "localhost:11435",  # フォールバック
        ]
        self.current_instance = 0
    
    async def get_available_instance(self):
        for i, instance in enumerate(self.ollama_instances):
            try:
                # ヘルスチェック
                response = await health_check(instance)
                if response.status_code == 200:
                    self.current_instance = i
                    return instance
            except Exception:
                continue
        raise Exception("No available Ollama instances")
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **モデル選択**: タスクに適したモデルサイズの選択
- **リソース監視**: メモリとCPU使用量の定期チェック
- **バックアップ**: 重要なモデルとデータのバックアップ
- **更新管理**: Ollama と ADK の定期的な更新

#### 注意点
- **モデルサイズ**: 大きなモデルは大量のメモリを消費
- **起動時間**: 初回モデルロードには時間がかかる
- **依存関係**: ローカル環境の設定に依存
- **スケーラビリティ**: 単一マシンの性能に制限される

### 7.4 他のプロジェクトへの応用

#### エッジ AI エージェント
```python
class EdgeAIAgent:
    def __init__(self):
        self.local_models = {
            "lightweight": "ollama_chat/gemma:2b",
            "balanced": "ollama_chat/mistral-small3.1", 
            "powerful": "ollama_chat/llama3.1:70b"
        }
    
    def select_model_by_resources(self):
        memory = psutil.virtual_memory()
        if memory.total < 8 * 1024**3:  # 8GB未満
            return self.local_models["lightweight"]
        elif memory.total < 32 * 1024**3:  # 32GB未満
            return self.local_models["balanced"]
        else:
            return self.local_models["powerful"]
```

この hello_world_ollama エージェントは、プライバシーと自律性を重視したローカル AI エージェント開発の基本パターンを提供します。特に機密データを扱うシステムや、インターネット接続が制限された環境での AI エージェント構築に有用です。