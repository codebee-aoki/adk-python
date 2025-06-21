# トークン使用量監視エージェント - 技術ドキュメント

## 概要

トークン使用量監視エージェント（`token_usage`）は、複数の LLM プロバイダー（OpenAI、Anthropic、Google Gemini）を使用したマルチモデル エージェント システムにおけるトークン使用量の監視とコスト管理を実演するエージェントです。各プロバイダーのトークン消費パターン、コスト分析、使用量最適化の手法を学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# マルチモデル トークン監視システム
root_agent = SequentialAgent(
    name='code_pipeline_agent',
    sub_agents=[
        roll_agent_with_openai,      # OpenAI GPT-4o
        roll_agent_with_claude,      # Anthropic Claude
        roll_agent_with_litellm_claude,  # LiteLLM経由のClaude
        roll_agent_with_gemini,      # Google Gemini
    ],
)
```

### 主要コンポーネント

#### 1. マルチプロバイダー エージェント構成

**OpenAI エージェント**:
```python
roll_agent_with_openai = LlmAgent(
    model=LiteLlm(model='openai/gpt-4o'),
    description='Handles rolling dice of different sizes.',
    name='roll_agent_with_openai',
    instruction="You are responsible for rolling dice based on the user's request...",
    tools=[roll_die],
)
```

**Anthropic Claude エージェント**:
```python
roll_agent_with_claude = LlmAgent(
    model=Claude(model='claude-3-7-sonnet@20250219'),
    description='Handles rolling dice of different sizes.',
    name='roll_agent_with_claude',
    instruction="You are responsible for rolling dice based on the user's request...",
    tools=[roll_die],
)
```

**LiteLLM 経由 Claude エージェント**:
```python
roll_agent_with_litellm_claude = LlmAgent(
    model=LiteLlm(model='vertex_ai/claude-3-7-sonnet'),
    description='Handles rolling dice of different sizes.',
    name='roll_agent_with_litellm_claude',
    instruction="You are responsible for rolling dice based on the user's request...",
    tools=[roll_die],
)
```

**Google Gemini エージェント**:
```python
roll_agent_with_gemini = LlmAgent(
    model='gemini-2.0-flash',
    description='Handles rolling dice of different sizes.',
    name='roll_agent_with_gemini',
    instruction="You are responsible for rolling dice based on the user's request...",
    tools=[roll_die],
)
```

#### 2. 共通ツール（トークン使用量追跡付き）
```python
def roll_die(sides: int, tool_context: ToolContext) -> int:
    """トークン使用量追跡付きサイコロ転がし"""
    result = random.randint(1, sides)
    
    # 状態管理
    if 'rolls' not in tool_context.state:
        tool_context.state['rolls'] = []
    tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
    
    # トークン使用量記録
    token_tracker.record_tool_usage('roll_die', tool_context.agent_name)
    
    return result
```

## トークン使用量監視システム

### 1. トークン追跡クラス

```python
class TokenUsageTracker:
    def __init__(self):
        self.usage_data = {
            'openai': {
                'total_tokens': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'requests': 0,
                'cost_usd': 0.0,
            },
            'claude': {
                'total_tokens': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'requests': 0,
                'cost_usd': 0.0,
            },
            'gemini': {
                'total_tokens': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'requests': 0,
                'cost_usd': 0.0,
            },
        }
        self.pricing = self.load_pricing_config()
    
    def load_pricing_config(self) -> dict:
        """プロバイダー別料金設定"""
        return {
            'openai': {
                'gpt-4o': {
                    'input_per_1k': 0.0050,   # $0.005 per 1K input tokens
                    'output_per_1k': 0.0150,  # $0.015 per 1K output tokens
                }
            },
            'claude': {
                'claude-3-7-sonnet': {
                    'input_per_1k': 0.0030,   # $0.003 per 1K input tokens
                    'output_per_1k': 0.0150,  # $0.015 per 1K output tokens
                }
            },
            'gemini': {
                'gemini-2.0-flash': {
                    'input_per_1k': 0.0001,   # $0.0001 per 1K input tokens
                    'output_per_1k': 0.0005,  # $0.0005 per 1K output tokens
                }
            },
        }
    
    def record_usage(self, provider: str, model: str, input_tokens: int, output_tokens: int):
        """トークン使用量の記録"""
        if provider not in self.usage_data:
            self.usage_data[provider] = {
                'total_tokens': 0, 'input_tokens': 0, 
                'output_tokens': 0, 'requests': 0, 'cost_usd': 0.0
            }
        
        # 使用量更新
        self.usage_data[provider]['input_tokens'] += input_tokens
        self.usage_data[provider]['output_tokens'] += output_tokens
        self.usage_data[provider]['total_tokens'] += (input_tokens + output_tokens)
        self.usage_data[provider]['requests'] += 1
        
        # コスト計算
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        self.usage_data[provider]['cost_usd'] += cost
    
    def calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """コスト計算"""
        if provider not in self.pricing or model not in self.pricing[provider]:
            return 0.0
        
        rates = self.pricing[provider][model]
        input_cost = (input_tokens / 1000) * rates['input_per_1k']
        output_cost = (output_tokens / 1000) * rates['output_per_1k']
        
        return input_cost + output_cost
```

### 2. リアルタイム監視

```python
class RealTimeTokenMonitor:
    def __init__(self, tracker: TokenUsageTracker):
        self.tracker = tracker
        self.alerts = []
        self.thresholds = {
            'daily_cost_limit': 100.0,      # $100/日
            'hourly_token_limit': 1000000,  # 1M tokens/時間
            'cost_per_request_limit': 1.0,  # $1/リクエスト
        }
    
    async def monitor_usage(self):
        """リアルタイム使用量監視"""
        while True:
            current_usage = self.tracker.get_current_usage()
            
            # しきい値チェック
            await self.check_thresholds(current_usage)
            
            # 使用パターン分析
            patterns = self.analyze_usage_patterns(current_usage)
            
            # 異常検知
            anomalies = self.detect_anomalies(current_usage)
            
            if anomalies:
                await self.handle_anomalies(anomalies)
            
            await asyncio.sleep(60)  # 1分間隔
    
    async def check_thresholds(self, usage: dict):
        """しきい値チェック"""
        total_daily_cost = sum(provider['cost_usd'] for provider in usage.values())
        
        if total_daily_cost > self.thresholds['daily_cost_limit']:
            alert = {
                'type': 'daily_cost_exceeded',
                'value': total_daily_cost,
                'threshold': self.thresholds['daily_cost_limit'],
                'timestamp': time.time(),
            }
            await self.send_alert(alert)
```

### 3. コスト最適化分析

```python
class CostOptimizer:
    def __init__(self, tracker: TokenUsageTracker):
        self.tracker = tracker
        
    def analyze_cost_efficiency(self) -> dict:
        """コスト効率分析"""
        usage_data = self.tracker.usage_data
        
        analysis = {
            'total_cost': sum(provider['cost_usd'] for provider in usage_data.values()),
            'cost_by_provider': {
                provider: data['cost_usd'] 
                for provider, data in usage_data.items()
            },
            'cost_per_request': {},
            'token_efficiency': {},
            'recommendations': [],
        }
        
        # プロバイダー別効率分析
        for provider, data in usage_data.items():
            if data['requests'] > 0:
                analysis['cost_per_request'][provider] = data['cost_usd'] / data['requests']
                analysis['token_efficiency'][provider] = data['total_tokens'] / data['cost_usd'] if data['cost_usd'] > 0 else 0
        
        # 最適化推奨事項
        analysis['recommendations'] = self.generate_recommendations(analysis)
        
        return analysis
    
    def generate_recommendations(self, analysis: dict) -> list:
        """最適化推奨事項の生成"""
        recommendations = []
        
        # 最も高コストなプロバイダーの特定
        if analysis['cost_by_provider']:
            most_expensive = max(analysis['cost_by_provider'].items(), key=lambda x: x[1])
            recommendations.append({
                'type': 'cost_reduction',
                'message': f"{most_expensive[0]} が最もコストが高い (${most_expensive[1]:.4f})",
                'action': '他のプロバイダーとの比較検討を推奨',
            })
        
        # トークン効率の分析
        if analysis['token_efficiency']:
            most_efficient = max(analysis['token_efficiency'].items(), key=lambda x: x[1])
            recommendations.append({
                'type': 'efficiency_optimization',
                'message': f"{most_efficient[0]} が最もトークン効率が良い ({most_efficient[1]:.2f} tokens/$)",
                'action': 'コスト重視のタスクでの使用を推奨',
            })
        
        return recommendations
```

## 実行フロー

### 1. マルチプロバイダー順次実行

**基本実行パターン**:
```text
User: "6面サイコロを転がしてください"

1. OpenAI GPT-4o エージェント実行
   ├─ Input tokens: ~50
   ├─ Output tokens: ~30
   ├─ Cost: ~$0.0007
   ├─ Result: "6面サイコロを転がした結果、4が出ました"

2. Claude 3.7 Sonnet エージェント実行
   ├─ Input tokens: ~80 (前の結果含む)
   ├─ Output tokens: ~35
   ├─ Cost: ~$0.0008
   ├─ Result: "サイコロの結果4を確認しました"

3. LiteLLM Claude エージェント実行
   ├─ Input tokens: ~120 (累積)
   ├─ Output tokens: ~40
   ├─ Cost: ~$0.0010
   ├─ Result: "前の結果を踏まえて追加分析"

4. Gemini 2.0 Flash エージェント実行
   ├─ Input tokens: ~160 (累積)
   ├─ Output tokens: ~45
   ├─ Cost: ~$0.0001
   ├─ Result: "全ての結果を統合した最終回答"

Total Cost: ~$0.0026
Total Tokens: ~545
```

## 実行例

### 基本的なトークン使用量監視

**監視付き実行**:
```python
# トークン監視開始
token_tracker = TokenUsageTracker()
monitor = RealTimeTokenMonitor(token_tracker)
monitoring_task = asyncio.create_task(monitor.monitor_usage())

# エージェント実行
response = await root_agent.invoke("8面サイコロを転がしてください")

# 使用量レポート生成
usage_report = token_tracker.generate_report()
print(f"総コスト: ${usage_report['total_cost']:.4f}")
print(f"最高効率プロバイダー: {usage_report['most_efficient_provider']}")
```

**コスト分析**:
```python
optimizer = CostOptimizer(token_tracker)
analysis = optimizer.analyze_cost_efficiency()

print("=== コスト効率分析 ===")
for provider, cost in analysis['cost_by_provider'].items():
    efficiency = analysis['token_efficiency'][provider]
    print(f"{provider}: ${cost:.4f} ({efficiency:.2f} tokens/$)")

print("\n=== 推奨事項 ===")
for rec in analysis['recommendations']:
    print(f"- {rec['message']}")
    print(f"  行動: {rec['action']}")
```

## 高度な実装例

### 1. 動的プロバイダー選択

```python
class IntelligentProviderSelector:
    def __init__(self, tracker: TokenUsageTracker):
        self.tracker = tracker
        self.performance_history = defaultdict(list)
        
    async def select_optimal_provider(self, task_complexity: str, budget_limit: float) -> str:
        """最適プロバイダーの選択"""
        providers = ['openai', 'claude', 'gemini']
        
        # タスク複雑度に基づく初期フィルタリング
        if task_complexity == 'high':
            providers = ['openai', 'claude']  # 高性能モデルのみ
        elif task_complexity == 'low':
            providers = ['gemini']  # コスト重視
        
        # 予算制約の適用
        affordable_providers = []
        for provider in providers:
            estimated_cost = self.estimate_cost(provider, task_complexity)
            if estimated_cost <= budget_limit:
                affordable_providers.append(provider)
        
        if not affordable_providers:
            raise ValueError(f"予算 ${budget_limit} 内で実行可能なプロバイダーがありません")
        
        # パフォーマンス履歴に基づく選択
        best_provider = self.select_by_performance(affordable_providers)
        return best_provider
    
    def estimate_cost(self, provider: str, complexity: str) -> float:
        """コスト予測"""
        base_tokens = {
            'low': 100,
            'medium': 300,
            'high': 800,
        }
        
        input_tokens = base_tokens[complexity]
        output_tokens = input_tokens * 0.5  # 出力は入力の50%と仮定
        
        return self.tracker.calculate_cost(provider, self.get_default_model(provider), input_tokens, output_tokens)
```

### 2. バッチ処理による効率化

```python
class BatchTokenOptimizer:
    def __init__(self, tracker: TokenUsageTracker):
        self.tracker = tracker
        self.batch_queue = []
        self.batch_size = 10
        
    async def process_batch(self, requests: list[str]) -> list[str]:
        """バッチ処理による効率化"""
        # リクエストをバッチに分割
        batches = [requests[i:i+self.batch_size] for i in range(0, len(requests), self.batch_size)]
        
        results = []
        total_savings = 0
        
        for batch in batches:
            # バッチ用の統合プロンプト作成
            combined_prompt = self.create_batch_prompt(batch)
            
            # 最もコスト効率の良いプロバイダーを選択
            optimal_provider = self.select_cheapest_provider()
            
            # バッチ実行
            batch_response = await self.execute_batch(optimal_provider, combined_prompt)
            
            # 結果を個別レスポンスに分解
            individual_results = self.parse_batch_response(batch_response, len(batch))
            results.extend(individual_results)
            
            # コスト節約の計算
            individual_cost = sum(self.estimate_individual_cost(req) for req in batch)
            batch_cost = self.tracker.get_last_request_cost()
            savings = individual_cost - batch_cost
            total_savings += savings
        
        print(f"バッチ処理により ${total_savings:.4f} 節約")
        return results
```

### 3. 使用量予算管理

```python
class TokenBudgetManager:
    def __init__(self, daily_budget: float, monthly_budget: float):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.daily_usage = 0.0
        self.monthly_usage = 0.0
        self.usage_history = []
        
    async def check_budget_availability(self, estimated_cost: float) -> dict:
        """予算可用性チェック"""
        check_result = {
            'approved': True,
            'remaining_daily': self.daily_budget - self.daily_usage,
            'remaining_monthly': self.monthly_budget - self.monthly_usage,
            'warnings': [],
            'suggestions': [],
        }
        
        # 日次予算チェック
        if self.daily_usage + estimated_cost > self.daily_budget:
            check_result['approved'] = False
            check_result['warnings'].append("日次予算を超過します")
            check_result['suggestions'].append("明日まで待つか、予算を増額してください")
        
        # 月次予算チェック
        if self.monthly_usage + estimated_cost > self.monthly_budget:
            check_result['approved'] = False
            check_result['warnings'].append("月次予算を超過します")
            
        # 予算残り80%アラート
        if self.daily_usage / self.daily_budget > 0.8:
            check_result['warnings'].append("日次予算の80%を使用済み")
            
        return check_result
    
    async def approve_expenditure(self, cost: float, provider: str, request_details: dict):
        """支出承認"""
        # 予算から減額
        self.daily_usage += cost
        self.monthly_usage += cost
        
        # 使用履歴に記録
        self.usage_history.append({
            'timestamp': time.time(),
            'cost': cost,
            'provider': provider,
            'details': request_details,
            'daily_total': self.daily_usage,
            'monthly_total': self.monthly_usage,
        })
        
        # 予算アラートチェック
        await self.check_budget_alerts()
```

## ダッシュボードとレポート

### 1. リアルタイムダッシュボード

```python
class TokenUsageDashboard:
    def __init__(self, tracker: TokenUsageTracker):
        self.tracker = tracker
        
    def generate_realtime_dashboard(self) -> dict:
        """リアルタイムダッシュボードデータ"""
        usage_data = self.tracker.usage_data
        
        dashboard = {
            'summary': {
                'total_requests': sum(data['requests'] for data in usage_data.values()),
                'total_tokens': sum(data['total_tokens'] for data in usage_data.values()),
                'total_cost': sum(data['cost_usd'] for data in usage_data.values()),
                'average_cost_per_request': 0,
            },
            'by_provider': {},
            'trends': self.calculate_trends(),
            'alerts': self.get_active_alerts(),
            'recommendations': self.get_cost_recommendations(),
        }
        
        # プロバイダー別詳細
        for provider, data in usage_data.items():
            dashboard['by_provider'][provider] = {
                'requests': data['requests'],
                'tokens': data['total_tokens'],
                'cost': data['cost_usd'],
                'avg_tokens_per_request': data['total_tokens'] / data['requests'] if data['requests'] > 0 else 0,
                'cost_per_1k_tokens': (data['cost_usd'] / data['total_tokens'] * 1000) if data['total_tokens'] > 0 else 0,
            }
        
        # 平均コスト計算
        total_requests = dashboard['summary']['total_requests']
        if total_requests > 0:
            dashboard['summary']['average_cost_per_request'] = dashboard['summary']['total_cost'] / total_requests
        
        return dashboard
```

### 2. 詳細分析レポート

```python
class DetailedUsageReport:
    def __init__(self, tracker: TokenUsageTracker):
        self.tracker = tracker
        
    def generate_comprehensive_report(self, period: str = 'daily') -> dict:
        """包括的使用レポート"""
        report = {
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'executive_summary': self.generate_executive_summary(),
            'detailed_usage': self.generate_detailed_usage(),
            'cost_analysis': self.generate_cost_analysis(),
            'efficiency_metrics': self.generate_efficiency_metrics(),
            'trends_and_patterns': self.analyze_trends_and_patterns(),
            'recommendations': self.generate_strategic_recommendations(),
            'appendices': {
                'raw_data': self.tracker.usage_data,
                'methodology': self.get_calculation_methodology(),
            }
        }
        
        return report
    
    def generate_executive_summary(self) -> dict:
        """エグゼクティブサマリー"""
        usage_data = self.tracker.usage_data
        
        total_cost = sum(data['cost_usd'] for data in usage_data.values())
        total_tokens = sum(data['total_tokens'] for data in usage_data.values())
        
        most_used_provider = max(usage_data.items(), key=lambda x: x[1]['requests'])[0]
        most_expensive_provider = max(usage_data.items(), key=lambda x: x[1]['cost_usd'])[0]
        
        return {
            'key_metrics': {
                'total_cost': total_cost,
                'total_tokens': total_tokens,
                'total_requests': sum(data['requests'] for data in usage_data.values()),
            },
            'insights': [
                f"最も使用頻度の高いプロバイダー: {most_used_provider}",
                f"最もコストの高いプロバイダー: {most_expensive_provider}",
                f"平均コスト/リクエスト: ${total_cost/sum(data['requests'] for data in usage_data.values()):.4f}",
            ],
            'cost_breakdown': {
                provider: data['cost_usd'] 
                for provider, data in usage_data.items()
            }
        }
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `main.py`: 実行エントリーポイント

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.agents.sequential_agent`: シーケンシャルエージェント
- `google.adk.models.anthropic_llm`: Anthropic Claude モデル
- `google.adk.models.lite_llm`: LiteLLM 統合
- `google.adk.tools.tool_context`: ツールコンテキスト
- `random`: 乱数生成（サイコロ機能）
- **外部プロバイダー API**: OpenAI、Anthropic、Google AI
- **監視ツール**: Prometheus、Grafana等（オプション）