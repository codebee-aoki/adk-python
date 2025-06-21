# テレメトリーエージェント - 技術ドキュメント

## 概要

テレメトリーエージェント（`telemetry`）は、ADK フレームワークのテレメトリー（遠隔測定）機能を実演するエージェントです。エージェントの実行メトリクス、パフォーマンス データ、ツール使用状況などの監視データを収集・送信し、運用環境でのエージェント監視とトラブルシューティングのパターンを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# テレメトリー対応エージェント
root_agent = Agent(
    model='gemini-2.0-flash',
    name='data_processing_agent',
    description='hello world agent that can roll a dice of 8 sides and check prime numbers.',
    instruction="...",  # サイコロと素数判定の指示
    tools=[roll_die, check_prime],
    
    # テレメトリー設定（コメントアウト例）
    # telemetry_config=TelemetryConfig(
    #     enabled=True,
    #     collection_interval=30,
    #     metrics_endpoint="https://monitoring.example.com/metrics",
    # ),
)
```

### 主要コンポーネント

#### 1. テレメトリーデータ収集
```python
# 収集される主要メトリクス
telemetry_metrics = {
    'execution_metrics': {
        'total_invocations': 0,           # 総実行回数
        'successful_invocations': 0,      # 成功実行回数
        'failed_invocations': 0,          # 失敗実行回数
        'average_response_time': 0.0,     # 平均応答時間
    },
    'tool_usage': {
        'roll_die_calls': 0,              # roll_die ツール呼び出し回数
        'check_prime_calls': 0,           # check_prime ツール呼び出し回数
        'tool_errors': 0,                 # ツールエラー回数
    },
    'model_metrics': {
        'tokens_used': 0,                 # 使用トークン数
        'model_calls': 0,                 # モデル呼び出し回数
        'model_errors': 0,                # モデルエラー回数
    },
    'resource_usage': {
        'memory_usage_mb': 0.0,           # メモリ使用量
        'cpu_usage_percent': 0.0,         # CPU 使用率
    }
}
```

#### 2. サイコロ転がしツール（テレメトリー付き）
```python
def roll_die(sides: int, tool_context: ToolContext) -> int:
    """テレメトリー対応サイコロ転がし"""
    start_time = time.time()
    
    try:
        result = random.randint(1, sides)
        
        # 状態管理
        if not 'rolls' in tool_context.state:
            tool_context.state['rolls'] = []
        tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
        
        # テレメトリーデータ記録
        execution_time = time.time() - start_time
        telemetry_logger.record_tool_usage('roll_die', execution_time, True)
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        telemetry_logger.record_tool_usage('roll_die', execution_time, False, str(e))
        raise
```

#### 3. 素数判定ツール（テレメトリー付き）
```python
async def check_prime(nums: list[int]) -> str:
    """テレメトリー対応素数判定"""
    start_time = time.time()
    
    try:
        primes = set()
        for number in nums:
            number = int(number)
            if number <= 1:
                continue
            is_prime = True
            for i in range(2, int(number**0.5) + 1):
                if number % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.add(number)
        
        result = (
            'No prime numbers found.'
            if not primes
            else f"{', '.join(str(num) for num in primes)} are prime numbers."
        )
        
        # テレメトリーデータ記録
        execution_time = time.time() - start_time
        telemetry_logger.record_tool_usage('check_prime', execution_time, True)
        telemetry_logger.record_prime_analysis(nums, list(primes))
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        telemetry_logger.record_tool_usage('check_prime', execution_time, False, str(e))
        raise
```

## テレメトリーシステム機能

### 1. メトリクス収集

**パフォーマンスメトリクス**:
```python
class PerformanceTelemetry:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'throughput_per_minute': 0,
            'concurrent_requests': 0,
            'error_rate': 0.0,
        }
    
    def record_request(self, start_time: float, end_time: float, success: bool):
        """リクエストのパフォーマンス記録"""
        response_time = end_time - start_time
        self.metrics['response_times'].append(response_time)
        
        # 移動平均の計算
        if len(self.metrics['response_times']) > 100:
            self.metrics['response_times'] = self.metrics['response_times'][-100:]
        
        # エラー率の更新
        total_requests = len(self.metrics['response_times'])
        failed_requests = sum(1 for rt in self.metrics['response_times'] if rt < 0)
        self.metrics['error_rate'] = failed_requests / total_requests if total_requests > 0 else 0
```

**使用量メトリクス**:
```python
class UsageTelemetry:
    def __init__(self):
        self.tool_usage = defaultdict(int)
        self.feature_usage = defaultdict(int)
        self.user_sessions = set()
    
    def record_tool_usage(self, tool_name: str, user_id: str = None):
        """ツール使用量の記録"""
        self.tool_usage[tool_name] += 1
        
        if user_id:
            self.user_sessions.add(user_id)
    
    def record_feature_usage(self, feature: str, user_id: str = None):
        """機能使用量の記録"""
        self.feature_usage[feature] += 1
```

### 2. リアルタイム監視

**ライブメトリクス**:
```python
class LiveTelemetry:
    def __init__(self, update_interval: int = 30):
        self.update_interval = update_interval
        self.current_metrics = {}
        self.metric_history = []
        
    async def start_monitoring(self):
        """リアルタイム監視開始"""
        while True:
            # システムメトリクス収集
            current_time = time.time()
            system_metrics = {
                'timestamp': current_time,
                'memory_usage': self.get_memory_usage(),
                'cpu_usage': self.get_cpu_usage(),
                'active_connections': self.get_active_connections(),
                'queue_size': self.get_queue_size(),
            }
            
            self.current_metrics = system_metrics
            self.metric_history.append(system_metrics)
            
            # 古いデータの削除（24時間分のみ保持）
            cutoff_time = current_time - (24 * 3600)
            self.metric_history = [
                m for m in self.metric_history 
                if m['timestamp'] > cutoff_time
            ]
            
            # メトリクス送信
            await self.send_metrics(system_metrics)
            
            await asyncio.sleep(self.update_interval)
```

### 3. アラートシステム

**しきい値監視**:
```python
class AlertingSystem:
    def __init__(self):
        self.alert_rules = {
            'high_error_rate': {'threshold': 0.05, 'enabled': True},
            'slow_response': {'threshold': 5.0, 'enabled': True},
            'high_memory_usage': {'threshold': 80.0, 'enabled': True},
            'tool_failure_rate': {'threshold': 0.10, 'enabled': True},
        }
        self.alert_history = []
    
    async def check_alerts(self, metrics: dict):
        """アラート条件のチェック"""
        alerts_triggered = []
        
        # エラー率チェック
        if (metrics.get('error_rate', 0) > self.alert_rules['high_error_rate']['threshold'] and
            self.alert_rules['high_error_rate']['enabled']):
            alerts_triggered.append({
                'type': 'high_error_rate',
                'value': metrics['error_rate'],
                'threshold': self.alert_rules['high_error_rate']['threshold'],
                'severity': 'warning',
            })
        
        # 応答時間チェック
        avg_response_time = sum(metrics.get('response_times', [])) / len(metrics.get('response_times', [1]))
        if (avg_response_time > self.alert_rules['slow_response']['threshold'] and
            self.alert_rules['slow_response']['enabled']):
            alerts_triggered.append({
                'type': 'slow_response',
                'value': avg_response_time,
                'threshold': self.alert_rules['slow_response']['threshold'],
                'severity': 'warning',
            })
        
        # アラート送信
        for alert in alerts_triggered:
            await self.send_alert(alert)
            self.alert_history.append({
                **alert,
                'timestamp': time.time(),
            })
```

## 実行例

### 基本的なテレメトリー収集

**テレメトリー有効化での実行**:
```python
# テレメトリー初期化
telemetry_collector = TelemetryCollector()
telemetry_collector.start()

# エージェント実行
response = await root_agent.invoke("6面サイコロを転がして素数判定してください")

# テレメトリーデータ確認
metrics = telemetry_collector.get_current_metrics()
print(f"実行時間: {metrics['last_execution_time']}秒")
print(f"ツール呼び出し: roll_die={metrics['roll_die_calls']}, check_prime={metrics['check_prime_calls']}")
print(f"メモリ使用量: {metrics['memory_usage_mb']}MB")
```

**継続的監視**:
```python
# 長期間の監視
monitoring_session = TelemetrySession(duration_hours=24)

for i in range(100):
    # 複数回実行でパターン分析
    await root_agent.invoke(f"{random.randint(4, 20)}面サイコロを転がして素数判定")
    await asyncio.sleep(random.uniform(1, 5))

# 監視結果の分析
analysis = monitoring_session.analyze_patterns()
print(f"平均応答時間: {analysis['avg_response_time']}秒")
print(f"ピーク使用量: {analysis['peak_memory_usage']}MB")
print(f"エラー率: {analysis['error_rate']*100:.2f}%")
```

## 高度な実装例

### 1. 分散テレメトリーシステム

```python
class DistributedTelemetry:
    def __init__(self, node_id: str, cluster_config: dict):
        self.node_id = node_id
        self.cluster_config = cluster_config
        self.local_metrics = {}
        self.cluster_metrics = {}
    
    async def collect_cluster_metrics(self):
        """クラスター全体のメトリクス収集"""
        cluster_data = {}
        
        for node in self.cluster_config['nodes']:
            try:
                node_metrics = await self.get_node_metrics(node['endpoint'])
                cluster_data[node['id']] = node_metrics
            except Exception as e:
                logger.error(f"Failed to collect metrics from {node['id']}: {e}")
        
        # 集約メトリクスの計算
        self.cluster_metrics = self.aggregate_metrics(cluster_data)
        return self.cluster_metrics
    
    def aggregate_metrics(self, node_data: dict) -> dict:
        """ノードメトリクスの集約"""
        aggregated = {
            'total_requests': sum(data.get('requests', 0) for data in node_data.values()),
            'total_errors': sum(data.get('errors', 0) for data in node_data.values()),
            'avg_response_time': sum(data.get('avg_response_time', 0) for data in node_data.values()) / len(node_data),
            'active_nodes': len([data for data in node_data.values() if data.get('status') == 'healthy']),
            'total_memory_usage': sum(data.get('memory_mb', 0) for data in node_data.values()),
        }
        
        return aggregated
```

### 2. カスタムメトリクス

```python
class CustomMetricsCollector:
    def __init__(self):
        self.business_metrics = {
            'dice_rolls_by_sides': defaultdict(int),
            'prime_numbers_found': [],
            'user_satisfaction_scores': [],
            'feature_adoption_rates': {},
        }
    
    def record_dice_roll(self, sides: int, result: int):
        """サイコロ転がしのビジネスメトリクス"""
        self.business_metrics['dice_rolls_by_sides'][sides] += 1
        
        # 高い目が出る確率の追跡
        if result > sides * 0.8:
            self.business_metrics.setdefault('high_rolls', 0)
            self.business_metrics['high_rolls'] += 1
    
    def record_prime_discovery(self, number: int, is_prime: bool):
        """素数発見のメトリクス"""
        if is_prime:
            self.business_metrics['prime_numbers_found'].append(number)
            
            # 大きな素数の発見
            if number > 100:
                self.business_metrics.setdefault('large_primes_found', 0)
                self.business_metrics['large_primes_found'] += 1
    
    def calculate_insights(self) -> dict:
        """ビジネスインサイトの計算"""
        prime_numbers = self.business_metrics['prime_numbers_found']
        
        insights = {
            'most_popular_dice_size': max(
                self.business_metrics['dice_rolls_by_sides'].items(),
                key=lambda x: x[1],
                default=(None, 0)
            )[0],
            'prime_discovery_rate': len(prime_numbers) / sum(self.business_metrics['dice_rolls_by_sides'].values()),
            'average_prime_value': sum(prime_numbers) / len(prime_numbers) if prime_numbers else 0,
            'largest_prime_found': max(prime_numbers) if prime_numbers else 0,
        }
        
        return insights
```

### 3. テレメトリーダッシュボード

```python
class TelemetryDashboard:
    def __init__(self, telemetry_collector):
        self.collector = telemetry_collector
        self.dashboard_data = {}
    
    async def generate_dashboard_data(self):
        """ダッシュボード用データ生成"""
        current_metrics = self.collector.get_current_metrics()
        historical_data = self.collector.get_historical_data(hours=24)
        
        self.dashboard_data = {
            'overview': {
                'status': self.determine_system_status(current_metrics),
                'uptime': self.calculate_uptime(),
                'total_requests_24h': sum(h.get('requests', 0) for h in historical_data),
                'current_rps': self.calculate_requests_per_second(current_metrics),
            },
            'performance': {
                'avg_response_time': current_metrics.get('avg_response_time', 0),
                'p95_response_time': self.calculate_percentile(historical_data, 'response_time', 95),
                'error_rate': current_metrics.get('error_rate', 0),
                'throughput_trend': self.calculate_throughput_trend(historical_data),
            },
            'resources': {
                'memory_usage': current_metrics.get('memory_usage_mb', 0),
                'cpu_usage': current_metrics.get('cpu_usage_percent', 0),
                'disk_usage': current_metrics.get('disk_usage_percent', 0),
                'network_io': current_metrics.get('network_io_mbps', 0),
            },
            'tools': {
                'tool_usage_distribution': self.collector.get_tool_usage_stats(),
                'tool_performance': self.collector.get_tool_performance_stats(),
                'tool_error_rates': self.collector.get_tool_error_rates(),
            },
            'alerts': {
                'active_alerts': self.collector.get_active_alerts(),
                'recent_alerts': self.collector.get_recent_alerts(hours=24),
                'alert_trends': self.calculate_alert_trends(historical_data),
            }
        }
        
        return self.dashboard_data
    
    async def export_dashboard(self, format: str = 'json'):
        """ダッシュボードデータのエクスポート"""
        data = await self.generate_dashboard_data()
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'html':
            return self.generate_html_dashboard(data)
        elif format == 'prometheus':
            return self.generate_prometheus_metrics(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

## データ送信と保存

### 1. メトリクス送信

```python
class MetricsExporter:
    def __init__(self, endpoints: dict):
        self.endpoints = endpoints
        self.export_queue = asyncio.Queue()
    
    async def export_metrics(self, metrics: dict, destination: str = 'all'):
        """メトリクスの送信"""
        export_tasks = []
        
        if destination == 'all' or destination == 'prometheus':
            export_tasks.append(self.export_to_prometheus(metrics))
        
        if destination == 'all' or destination == 'elasticsearch':
            export_tasks.append(self.export_to_elasticsearch(metrics))
        
        if destination == 'all' or destination == 'datadog':
            export_tasks.append(self.export_to_datadog(metrics))
        
        # 並列送信
        results = await asyncio.gather(*export_tasks, return_exceptions=True)
        return results
    
    async def export_to_prometheus(self, metrics: dict):
        """Prometheus へのメトリクス送信"""
        prometheus_format = self.convert_to_prometheus_format(metrics)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoints['prometheus'], 
                data=prometheus_format,
                headers={'Content-Type': 'text/plain'}
            ) as response:
                return await response.text()
    
    def convert_to_prometheus_format(self, metrics: dict) -> str:
        """Prometheus 形式への変換"""
        lines = []
        timestamp = int(time.time() * 1000)
        
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                lines.append(f"{metric_name} {value} {timestamp}")
        
        return '\n'.join(lines)
```

### 2. ローカルストレージ

```python
class LocalTelemetryStorage:
    def __init__(self, storage_path: str, retention_days: int = 30):
        self.storage_path = storage_path
        self.retention_days = retention_days
        
    async def store_metrics(self, metrics: dict):
        """メトリクスのローカル保存"""
        timestamp = datetime.now()
        filename = f"metrics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        # メトリクスデータの準備
        storage_data = {
            'timestamp': timestamp.isoformat(),
            'metrics': metrics,
            'metadata': {
                'agent_version': self.get_agent_version(),
                'system_info': self.get_system_info(),
            }
        }
        
        # ファイルに保存
        os.makedirs(self.storage_path, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(storage_data, f, indent=2, default=str)
    
    async def cleanup_old_data(self):
        """古いデータのクリーンアップ"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for filename in os.listdir(self.storage_path):
            if filename.startswith('metrics_'):
                filepath = os.path.join(self.storage_path, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    logger.info(f"Removed old telemetry file: {filename}")
```

## パフォーマンス最適化

### 1. 非同期データ収集

```python
class AsyncTelemetryCollector:
    def __init__(self, batch_size: int = 100, flush_interval: int = 60):
        self.metric_queue = asyncio.Queue()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.running = False
    
    async def start_collection(self):
        """非同期データ収集開始"""
        self.running = True
        
        # バッチ処理タスク
        batch_task = asyncio.create_task(self.batch_processor())
        
        # 定期フラッシュタスク
        flush_task = asyncio.create_task(self.periodic_flush())
        
        await asyncio.gather(batch_task, flush_task)
    
    async def batch_processor(self):
        """バッチ処理"""
        batch = []
        
        while self.running:
            try:
                # タイムアウト付きでメトリクス取得
                metric = await asyncio.wait_for(
                    self.metric_queue.get(), 
                    timeout=1.0
                )
                batch.append(metric)
                
                # バッチサイズに達したら処理
                if len(batch) >= self.batch_size:
                    await self.process_batch(batch)
                    batch = []
                    
            except asyncio.TimeoutError:
                # タイムアウト時も蓄積されたバッチを処理
                if batch:
                    await self.process_batch(batch)
                    batch = []
    
    async def process_batch(self, batch: list):
        """バッチデータの処理"""
        # 集約処理
        aggregated_metrics = self.aggregate_batch(batch)
        
        # 外部システムへの送信
        await self.export_metrics(aggregated_metrics)
```

### 2. メモリ効率化

```python
class MemoryEfficientTelemetry:
    def __init__(self, max_memory_mb: int = 100):
        self.max_memory_mb = max_memory_mb
        self.metric_buffer = collections.deque(maxlen=10000)
        self.compression_enabled = True
    
    def add_metric(self, metric: dict):
        """メモリ効率的なメトリクス追加"""
        # メモリ使用量チェック
        current_memory = self.get_current_memory_usage()
        if current_memory > self.max_memory_mb:
            self.compress_old_data()
        
        # 必要な情報のみ保持
        compressed_metric = self.compress_metric(metric)
        self.metric_buffer.append(compressed_metric)
    
    def compress_metric(self, metric: dict) -> dict:
        """メトリクスの圧縮"""
        # 高精度が不要な値の丸め
        compressed = {}
        for key, value in metric.items():
            if isinstance(value, float):
                compressed[key] = round(value, 3)
            elif isinstance(value, str) and len(value) > 100:
                compressed[key] = value[:100] + "..."
            else:
                compressed[key] = value
        
        return compressed
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `main.py`: 実行エントリーポイント

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.tools.tool_context`: ツールコンテキスト
- `google.genai.types`: Google AI タイプ定義
- `random`: 乱数生成（サイコロ機能）
- **テレメトリーライブラリ**: OpenTelemetry、Prometheus等（オプション）
- **監視システム**: Datadog、New Relic、Grafana等（オプション）