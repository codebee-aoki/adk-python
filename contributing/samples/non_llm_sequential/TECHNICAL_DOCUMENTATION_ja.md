# 非LLMシーケンシャルエージェント - 技術ドキュメント

## 概要

非LLMシーケンシャルエージェント（`non_llm_sequential`）は、Large Language Model を使用せずにシンプルな応答ロジックを持つ複数のエージェントを順次実行する軽量なマルチエージェントシステムです。基本的なシーケンシャル実行パターンと、LLM なしでのエージェント構築方法を実演し、計算リソースを抑えた軽量な自動化システムの実装方法を学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# 非LLMシーケンシャルエージェント構成
from google.adk.agents import Agent
from google.adk.agents import SequentialAgent

# サブエージェント1: 単純な応答
sub_agent_1 = Agent(
    name='sub_agent_1',
    description='No.1 sub agent.',
    model='gemini-2.0-flash-001',
    instruction='JUST SAY 1.',  # 固定応答
)

# サブエージェント2: 単純な応答  
sub_agent_2 = Agent(
    name='sub_agent_2',
    description='No.2 sub agent.',
    model='gemini-2.0-flash-001',
    instruction='JUST SAY 2.',  # 固定応答
)

# シーケンシャル実行エージェント
sequential_agent = SequentialAgent(
    name='sequential_agent',
    sub_agents=[sub_agent_1, sub_agent_2],  # 順次実行
)

root_agent = sequential_agent
```

### 主要コンポーネント

#### 1. サブエージェント
```python
# 最小限のエージェント定義
sub_agent = Agent(
    name='agent_name',           # エージェント識別名
    description='agent_desc',    # エージェントの説明
    model='gemini-2.0-flash-001', # 使用モデル（最小リソース）
    instruction='SIMPLE_TASK',   # 単純なタスク指示
)
```

#### 2. SequentialAgent
```python
from google.adk.agents import SequentialAgent

sequential_agent = SequentialAgent(
    name='sequential_agent',          # シーケンシャルエージェント名
    sub_agents=[agent1, agent2, ...], # 実行順序でエージェントを配列定義
)
```

## 実行フロー

### 1. シーケンシャル実行パターン

**基本実行フロー**:
```text
User Input: "実行してください"
↓
SequentialAgent 開始
↓
sub_agent_1 実行
├─ instruction: "JUST SAY 1."
├─ model: gemini-2.0-flash-001  
├─ output: "1"
↓
sub_agent_2 実行
├─ instruction: "JUST SAY 2."
├─ model: gemini-2.0-flash-001
├─ output: "2"
↓
統合結果: "1\n2"
```

### 2. エージェント間の状態管理

**状態の継承**:
```text
sub_agent_1
├─ 入力: ユーザークエリ
├─ 処理: "JUST SAY 1."
├─ 出力: "1"
├─ 状態: {agent_1_executed: true}
↓
sub_agent_2  
├─ 入力: sub_agent_1 の出力 + 元のクエリ
├─ 処理: "JUST SAY 2."
├─ 出力: "2"
├─ 状態: {agent_1_executed: true, agent_2_executed: true}
```

## 使用例

### 基本的な実行

**シンプルな順次実行**:
```python
response = await root_agent.invoke("何か実行してください")

# 実行結果:
# sub_agent_1: "1"
# sub_agent_2: "2"
# 
# 最終出力: 
# "1
#  2"
```

**複数回の実行**:
```python
# 1回目
response1 = await root_agent.invoke("テスト1")  # "1\n2"

# 2回目  
response2 = await root_agent.invoke("テスト2")  # "1\n2"

# 毎回同じパターンで実行される
```

## 高度な実装例

### 1. データ処理パイプライン

```python
# データ検証エージェント
data_validator = Agent(
    name='data_validator',
    model='gemini-2.0-flash-001',
    instruction='Check if input data is valid. Return "VALID" if valid, "INVALID" if not.',
)

# データ変換エージェント
data_transformer = Agent(
    name='data_transformer', 
    model='gemini-2.0-flash-001',
    instruction='Transform the input data to uppercase format.',
)

# データ保存エージェント
data_saver = Agent(
    name='data_saver',
    model='gemini-2.0-flash-001', 
    instruction='Confirm data is saved. Return "SAVED".',
)

# データ処理パイプライン
data_pipeline = SequentialAgent(
    name='data_processing_pipeline',
    sub_agents=[data_validator, data_transformer, data_saver],
)
```

### 2. 承認ワークフロー

```python
# 申請内容確認
request_checker = Agent(
    name='request_checker',
    model='gemini-2.0-flash-001',
    instruction='Review the request and return "CHECKED".',
)

# 承認者1
approver_1 = Agent(
    name='first_approver',
    model='gemini-2.0-flash-001',
    instruction='First level approval. Return "APPROVED_L1".',
)

# 承認者2
approver_2 = Agent(
    name='second_approver', 
    model='gemini-2.0-flash-001',
    instruction='Second level approval. Return "APPROVED_L2".',
)

# 最終確認
final_confirmer = Agent(
    name='final_confirmer',
    model='gemini-2.0-flash-001',
    instruction='Final confirmation. Return "CONFIRMED".',
)

# 承認ワークフロー
approval_workflow = SequentialAgent(
    name='approval_workflow',
    sub_agents=[request_checker, approver_1, approver_2, final_confirmer],
)
```

### 3. テスト実行シーケンス

```python
# テスト準備
test_setup = Agent(
    name='test_setup',
    model='gemini-2.0-flash-001',
    instruction='Prepare test environment. Return "SETUP_COMPLETE".',
)

# テスト実行
test_runner = Agent(
    name='test_runner',
    model='gemini-2.0-flash-001', 
    instruction='Run tests. Return "TESTS_PASSED" or "TESTS_FAILED".',
)

# テスト結果レポート
test_reporter = Agent(
    name='test_reporter',
    model='gemini-2.0-flash-001',
    instruction='Generate test report. Return "REPORT_GENERATED".',
)

# テストクリーンアップ
test_cleanup = Agent(
    name='test_cleanup',
    model='gemini-2.0-flash-001',
    instruction='Clean up test environment. Return "CLEANUP_COMPLETE".',
)

# テスト実行シーケンス
test_sequence = SequentialAgent(
    name='test_automation_sequence',
    sub_agents=[test_setup, test_runner, test_reporter, test_cleanup],
)
```

## 軽量化のメリット

### 1. リソース効率性

**計算リソース削減**:
```python
# 従来の複雑なエージェント
complex_agent = Agent(
    model='gemini-2.5-pro',  # 高性能モデル
    instruction="""
    You are a sophisticated AI assistant that...
    [複雑な指示文 1000+ words]
    """,
    tools=[tool1, tool2, tool3, ...],  # 多数のツール
)

# 軽量エージェント
lightweight_agent = Agent(
    model='gemini-2.0-flash-001',  # 軽量モデル
    instruction='SIMPLE_TASK',     # 単純指示
    tools=[],                      # ツールなし
)
```

### 2. 予測可能性

**固定的な応答パターン**:
```python
# 毎回同じ出力が保証される
responses = []
for i in range(10):
    response = await simple_agent.invoke("test")
    responses.append(response)

# responses = ["1", "1", "1", ...] (一貫性)
```

### 3. デバッグとテストの容易性

**シンプルなテストケース**:
```python
import pytest

@pytest.mark.asyncio
async def test_sequential_agent():
    """シーケンシャルエージェントのテスト"""
    # 予期される出力が明確
    expected_output = "1\n2"
    
    actual_output = await root_agent.invoke("test")
    
    assert actual_output.strip() == expected_output
```

## 実践的な応用例

### 1. CI/CD パイプライン

```python
class CICDPipeline:
    def __init__(self):
        self.stages = [
            self.create_checkout_agent(),
            self.create_build_agent(),
            self.create_test_agent(),
            self.create_deploy_agent(),
        ]
        
        self.pipeline = SequentialAgent(
            name='cicd_pipeline',
            sub_agents=self.stages
        )
    
    def create_checkout_agent(self):
        return Agent(
            name='checkout',
            model='gemini-2.0-flash-001',
            instruction='Checkout code from repository. Return "CHECKOUT_SUCCESS".',
        )
    
    def create_build_agent(self):
        return Agent(
            name='build',
            model='gemini-2.0-flash-001',
            instruction='Build application. Return "BUILD_SUCCESS".',
        )
    
    async def run_pipeline(self, commit_hash: str):
        """パイプライン実行"""
        return await self.pipeline.invoke(f"Process commit {commit_hash}")
```

### 2. データ処理フロー

```python
class DataProcessingFlow:
    def __init__(self):
        self.processors = [
            self.create_extractor(),
            self.create_transformer(), 
            self.create_loader(),
        ]
        
        self.etl_pipeline = SequentialAgent(
            name='etl_pipeline',
            sub_agents=self.processors
        )
    
    def create_extractor(self):
        """データ抽出エージェント"""
        return Agent(
            name='extractor',
            model='gemini-2.0-flash-001',
            instruction='Extract data from source. Return "EXTRACTED".',
        )
    
    def create_transformer(self):
        """データ変換エージェント"""
        return Agent(
            name='transformer',
            model='gemini-2.0-flash-001',
            instruction='Transform extracted data. Return "TRANSFORMED".',
        )
    
    def create_loader(self):
        """データロードエージェント"""
        return Agent(
            name='loader',
            model='gemini-2.0-flash-001',
            instruction='Load transformed data to destination. Return "LOADED".',
        )
```

### 3. 承認チェーンシステム

```python
class ApprovalChain:
    def __init__(self, approval_levels: list[str]):
        self.approvers = []
        
        for i, level in enumerate(approval_levels):
            approver = Agent(
                name=f'approver_{i+1}',
                model='gemini-2.0-flash-001',
                instruction=f'Review and approve at {level} level. Return "APPROVED_{level.upper()}".',
            )
            self.approvers.append(approver)
        
        self.approval_chain = SequentialAgent(
            name='approval_chain',
            sub_agents=self.approvers
        )
    
    async def process_approval(self, request: str):
        """承認プロセス実行"""
        return await self.approval_chain.invoke(f"Approval request: {request}")

# 使用例
approval_system = ApprovalChain(['manager', 'director', 'ceo'])
result = await approval_system.process_approval("Budget increase request")
```

## パフォーマンス最適化

### 1. 並列化の検討

```python
# シーケンシャルな依存関係がない場合は並列実行も可能
from google.adk.agents import ParallelAgent

# 独立したタスクの場合
parallel_tasks = ParallelAgent(
    name='parallel_tasks',
    sub_agents=[
        independent_task_1,
        independent_task_2, 
        independent_task_3,
    ]
)
```

### 2. キャッシュ機能

```python
class CachedSequentialAgent:
    def __init__(self, sequential_agent):
        self.agent = sequential_agent
        self.cache = {}
    
    async def invoke_with_cache(self, input_text: str):
        """キャッシュ付き実行"""
        cache_key = hash(input_text)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self.agent.invoke(input_text)
        self.cache[cache_key] = result
        
        return result
```

### 3. バッチ処理

```python
class BatchSequentialProcessor:
    async def process_batch(self, inputs: list[str]):
        """バッチ処理"""
        tasks = []
        
        for input_text in inputs:
            task = self.agent.invoke(input_text)
            tasks.append(task)
        
        # 並列実行でスループット向上
        results = await asyncio.gather(*tasks)
        return results
```

## 制約と考慮事項

### 1. 機能の制限
- 複雑な推論能力は期待できない
- 動的な応答生成は限定的
- コンテキストの理解は浅い

### 2. 使用場面
- 定型的なワークフロー
- 単純な自動化タスク
- 軽量なテストケース
- プロトタイプ開発

### 3. スケーラビリティ
- エージェント数の増加による管理の複雑化
- シーケンシャル実行による処理時間の増大
- エラー処理の難しさ

## 関連ファイル

- `agent.py`: メインエージェント実装

## 依存関係

- `google.adk.agents`: エージェント基底クラス
- `google.adk.agents.SequentialAgent`: シーケンシャル実行エージェント
- Gemini 2.0 Flash モデル: 軽量LLMモデル