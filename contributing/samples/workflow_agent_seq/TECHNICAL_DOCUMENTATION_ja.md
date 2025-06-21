# ワークフローシーケンシャルエージェント - 技術ドキュメント

## 概要

ワークフローシーケンシャルエージェント（`workflow_agent_seq`）は、コード開発ワークフローを3段階のシーケンシャル処理で実現するマルチエージェントシステムです。コード生成→レビュー→リファクタリングの完全な開発パイプラインを自動化し、各段階での状態管理、エージェント間データ受け渡し、出力キーによる構造化データ管理の実装パターンを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# 3段階コード開発ワークフロー
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[
        code_writer_agent,      # 1. コード生成
        code_reviewer_agent,    # 2. コードレビュー
        code_refactorer_agent,  # 3. リファクタリング
    ],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
)

root_agent = code_pipeline_agent
```

### 主要コンポーネント

#### 1. コード生成エージェント
```python
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model="gemini-1.5-flash",
    instruction="""You are a Python Code Generator.
Based *only* on the user's request, write Python code that fulfills the requirement.
Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```).
Do not add any other text before or after the code block.""",
    description="Writes initial Python code based on a specification.",
    output_key="generated_code",  # 状態管理用キー
)
```

#### 2. コードレビューエージェント
```python
code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",
    model="gemini-2.0-flash",
    instruction="""You are an expert Python Code Reviewer.
Your task is to provide constructive feedback on the provided code.

**Code to Review:**
```python
{generated_code}
```

**Review Criteria:**
1. **Correctness:** Does the code work as intended? Are there logic errors?
2. **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
3. **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
4. **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
5. **Best Practices:** Does the code follow common Python best practices?

**Output:**
Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
If the code is excellent and requires no changes, simply state: "No major issues found."
Output *only* the review comments or the "No major issues" statement.""",
    description="Reviews code and provides feedback.",
    output_key="review_comments",  # 状態管理用キー
)
```

#### 3. コードリファクタリングエージェント
```python
code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",
    model="gemini-2.0-flash",
    instruction="""You are a Python Code Refactoring AI.
Your goal is to improve the given Python code based on the provided review comments.

**Original Code:**
```python
{generated_code}
```

**Review Comments:**
{review_comments}

**Task:**
Carefully apply the suggestions from the review comments to refactor the original code.
If the review comments state "No major issues found," return the original code unchanged.
Ensure the final code is complete, functional, and includes necessary imports and docstrings.

**Output:**
Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```).
Do not add any other text before or after the code block.""",
    description="Refactors code based on review comments.",
    output_key="refactored_code",  # 状態管理用キー
)
```

## 状態管理システム

### 1. 出力キー（output_key）による状態管理

**状態データの構造**:
```python
# ワークフロー実行中の状態
workflow_state = {
    'generated_code': "...",     # コード生成エージェントの出力
    'review_comments': "...",    # レビューエージェントの出力
    'refactored_code': "...",    # リファクタリングエージェントの出力
}
```

**状態キーインジェクション**:
```python
# 指示文での状態参照
instruction_template = """
**Original Code:**
```python
{generated_code}
```

**Review Comments:**
{review_comments}
"""
# {generated_code} と {review_comments} は実行時に実際の値で置換
```

### 2. エージェント間データフロー

**データ受け渡しパターン**:
```text
User Request: "ソート関数を実装してください"

1. CodeWriterAgent
   ├─ 入力: ユーザーリクエスト
   ├─ 処理: Python コード生成
   ├─ 出力: state['generated_code'] = "def sort_list(lst): ..."
   
2. CodeReviewerAgent
   ├─ 入力: ユーザーリクエスト + state['generated_code']
   ├─ 処理: コードレビュー実行
   ├─ 出力: state['review_comments'] = "• エラーハンドリングを追加..."
   
3. CodeRefactorerAgent
   ├─ 入力: ユーザーリクエスト + state['generated_code'] + state['review_comments']
   ├─ 処理: レビュー指摘事項の反映
   ├─ 出力: state['refactored_code'] = "def sort_list(lst): if not lst: ..."
```

## 実行フロー

### 1. 完全ワークフロー実行

**基本実行例**:
```text
User: "フィボナッチ数列を生成する関数を作成してください"

Stage 1: Code Generation
├─ Agent: CodeWriterAgent (gemini-1.5-flash)
├─ Task: Python コード生成
├─ Output: 
   def fibonacci(n):
       if n <= 1:
           return n
       return fibonacci(n-1) + fibonacci(n-2)

Stage 2: Code Review
├─ Agent: CodeReviewerAgent (gemini-2.0-flash)
├─ Input: 生成されたコード
├─ Analysis: 正確性、可読性、効率性、エッジケース、ベストプラクティス
├─ Output:
   • 効率性の問題: 再帰実装は大きなnで非効率
   • エッジケース: 負の値の処理が未実装
   • 最適化: メモ化またはイテレーティブ実装を推奨

Stage 3: Code Refactoring
├─ Agent: CodeRefactorerAgent (gemini-2.0-flash)
├─ Input: 元コード + レビューコメント
├─ Task: レビュー指摘事項の改善
├─ Output:
   def fibonacci(n):
       \"\"\"Generate the nth Fibonacci number.\"\"\"
       if n < 0:
           raise ValueError("n must be non-negative")
       if n <= 1:
           return n
       
       a, b = 0, 1
       for _ in range(2, n + 1):
           a, b = b, a + b
       return b
```

### 2. エラーハンドリングフロー

**レビューで問題なしの場合**:
```text
Stage 2: Code Review Result
├─ Output: "No major issues found."

Stage 3: Code Refactoring
├─ Logic: "No major issues found" の検出
├─ Action: 元のコードをそのまま返却
├─ Output: 元の generated_code と同一
```

## 高度な実装例

### 1. 拡張ワークフローシステム

```python
class ExtendedCodeWorkflow:
    def __init__(self):
        # 基本3段階に加えて追加段階
        self.test_writer_agent = self.create_test_writer_agent()
        self.documentation_agent = self.create_documentation_agent()
        self.security_reviewer_agent = self.create_security_reviewer_agent()
        
        # 拡張ワークフロー
        self.extended_pipeline = SequentialAgent(
            name="ExtendedCodePipeline",
            sub_agents=[
                self.code_writer_agent,
                self.code_reviewer_agent,
                self.code_refactorer_agent,
                self.test_writer_agent,        # 4. テストコード生成
                self.documentation_agent,      # 5. ドキュメント生成
                self.security_reviewer_agent,  # 6. セキュリティレビュー
            ],
        )
    
    def create_test_writer_agent(self):
        return LlmAgent(
            name="TestWriterAgent",
            model="gemini-2.0-flash",
            instruction="""You are a Python Test Writer.
Write comprehensive unit tests for the provided code.

**Code to Test:**
```python
{refactored_code}
```

Generate pytest-compatible test functions that cover:
1. Normal use cases
2. Edge cases
3. Error conditions
4. Boundary values

Output *only* the test code in a single code block.""",
            output_key="test_code",
        )
    
    def create_documentation_agent(self):
        return LlmAgent(
            name="DocumentationAgent",
            model="gemini-2.0-flash",
            instruction="""You are a Technical Documentation Writer.
Create comprehensive documentation for the provided code.

**Code:**
```python
{refactored_code}
```

**Tests:**
```python
{test_code}
```

Generate documentation including:
1. Function/class descriptions
2. Parameter explanations
3. Return value descriptions
4. Usage examples
5. Performance considerations

Output in Markdown format.""",
            output_key="documentation",
        )
```

### 2. 条件分岐ワークフロー

```python
class ConditionalWorkflow:
    def __init__(self):
        self.complexity_analyzer = self.create_complexity_analyzer()
        
    async def execute_adaptive_workflow(self, user_request: str):
        """複雑度に応じたワークフロー選択"""
        # 複雑度分析
        complexity = await self.analyze_complexity(user_request)
        
        if complexity == 'simple':
            # シンプルなコード: 生成→軽量レビュー
            pipeline = SequentialAgent(
                name="SimpleWorkflow",
                sub_agents=[
                    self.create_simple_code_writer(),
                    self.create_lightweight_reviewer(),
                ],
            )
        elif complexity == 'medium':
            # 標準的なワークフロー
            pipeline = self.create_standard_pipeline()
        else:  # complex
            # 複雑なコード: 完全ワークフロー + 追加検証
            pipeline = SequentialAgent(
                name="ComplexWorkflow",
                sub_agents=[
                    self.code_writer_agent,
                    self.code_reviewer_agent,
                    self.code_refactorer_agent,
                    self.create_performance_analyzer(),
                    self.create_security_auditor(),
                    self.create_final_validator(),
                ],
            )
        
        return await pipeline.invoke(user_request)
    
    async def analyze_complexity(self, request: str) -> str:
        """リクエストの複雑度分析"""
        complexity_indicators = {
            'simple': ['hello world', '単純な計算', 'basic function'],
            'medium': ['データ処理', 'API呼び出し', 'ファイル操作'],
            'complex': ['アルゴリズム', 'パフォーマンス', 'マルチスレッド', 'セキュリティ'],
        }
        
        request_lower = request.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in request_lower for indicator in indicators):
                return level
        
        return 'medium'  # デフォルト
```

### 3. 品質ゲート機能

```python
class QualityGateWorkflow:
    def __init__(self):
        self.quality_metrics = {
            'cyclomatic_complexity': 10,     # 循環的複雑度
            'line_count': 100,               # 行数制限
            'test_coverage': 80,             # テストカバレッジ
            'security_score': 8,             # セキュリティスコア
        }
    
    async def execute_with_quality_gates(self, user_request: str):
        """品質ゲート付きワークフロー"""
        workflow_state = {}
        
        # Stage 1: コード生成
        code_result = await self.code_writer_agent.invoke(user_request)
        workflow_state['generated_code'] = code_result
        
        # Quality Gate 1: 基本品質チェック
        if not await self.check_basic_quality(workflow_state['generated_code']):
            # 品質不足: 再生成
            code_result = await self.regenerate_with_constraints(user_request)
            workflow_state['generated_code'] = code_result
        
        # Stage 2: レビュー
        review_result = await self.code_reviewer_agent.invoke_with_state(user_request, workflow_state)
        workflow_state['review_comments'] = review_result
        
        # Quality Gate 2: レビュー品質チェック
        if await self.has_critical_issues(workflow_state['review_comments']):
            # 重大な問題: 追加レビューまたは再生成
            return await self.handle_critical_issues(user_request, workflow_state)
        
        # Stage 3: リファクタリング
        refactor_result = await self.code_refactorer_agent.invoke_with_state(user_request, workflow_state)
        workflow_state['refactored_code'] = refactor_result
        
        # Quality Gate 3: 最終品質チェック
        final_quality = await self.assess_final_quality(workflow_state['refactored_code'])
        if final_quality['overall_score'] < 8:
            # 品質不足: 追加改善
            return await self.additional_improvement_cycle(user_request, workflow_state)
        
        return workflow_state['refactored_code']
    
    async def check_basic_quality(self, code: str) -> bool:
        """基本品質チェック"""
        quality_checks = {
            'has_docstring': '"""' in code or "'''" in code,
            'proper_indentation': not code.startswith(' '),
            'reasonable_length': len(code.split('\n')) <= self.quality_metrics['line_count'],
            'no_obvious_errors': 'syntax error' not in code.lower(),
        }
        
        return all(quality_checks.values())
```

## パフォーマンス最適化

### 1. 並列処理最適化

```python
class OptimizedWorkflow:
    async def parallel_review_stage(self, code: str):
        """並列レビュー処理"""
        # 複数の専門レビューを並列実行
        review_tasks = [
            self.security_reviewer.invoke(code),      # セキュリティレビュー
            self.performance_reviewer.invoke(code),   # パフォーマンスレビュー
            self.style_reviewer.invoke(code),         # スタイルレビュー
            self.logic_reviewer.invoke(code),         # ロジックレビュー
        ]
        
        # 並列実行
        reviews = await asyncio.gather(*review_tasks)
        
        # レビュー結果の統合
        consolidated_review = self.consolidate_reviews(reviews)
        return consolidated_review
```

### 2. キャッシュ機能

```python
class CachedWorkflow:
    def __init__(self):
        self.code_cache = {}
        self.review_cache = {}
    
    async def cached_code_generation(self, request: str):
        """キャッシュ付きコード生成"""
        request_hash = hash(request)
        
        if request_hash in self.code_cache:
            return self.code_cache[request_hash]
        
        result = await self.code_writer_agent.invoke(request)
        self.code_cache[request_hash] = result
        
        return result
```

### 3. 段階的改善

```python
class IterativeImprovementWorkflow:
    async def iterative_refinement(self, user_request: str, max_iterations: int = 3):
        """段階的改善ワークフロー"""
        current_code = await self.initial_code_generation(user_request)
        
        for iteration in range(max_iterations):
            # レビュー実行
            review = await self.detailed_review(current_code)
            
            # 改善の必要性判定
            if self.is_satisfactory(review):
                break
            
            # コード改善
            current_code = await self.improve_code(current_code, review)
            
            # 改善度合いの測定
            improvement_score = await self.measure_improvement(current_code)
            
            if improvement_score < 0.1:  # 改善が少ない場合は終了
                break
        
        return current_code
```

## 実行例とベストプラクティス

### 基本的な使用方法

```python
response = await root_agent.invoke("二分探索アルゴリズムを実装してください")

# 期待される実行フロー:
# 1. 基本的な二分探索コード生成
# 2. アルゴリズムの正確性、効率性、エッジケースの確認
# 3. レビュー指摘事項を反映した最終コード
```

### 複雑な要件の処理

```python
complex_request = """
ウェブスクレイピング用のクラスを作成してください。
以下の要件を満たす必要があります：
- レート制限の実装
- エラーハンドリング
- ログ機能
- 設定可能なタイムアウト
- ユーザーエージェントのランダム化
"""

response = await root_agent.invoke(complex_request)

# 期待される改善点:
# - セキュリティ考慮事項
# - パフォーマンス最適化
# - 拡張性の確保
# - 適切なドキュメンテーション
```

## 関連ファイル

- `agent.py`: メインワークフローエージェント実装
- `main.py`: 実行エントリーポイント
- `sample.output`: 実行例出力ファイル
- `README.md`: 英語版ドキュメント
- `README_ja.md`: 日本語版ドキュメント

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.agents.sequential_agent`: シーケンシャルエージェント
- Gemini 1.5 Flash: コード生成用モデル
- Gemini 2.0 Flash: レビュー・リファクタリング用モデル