# セッション状態管理エージェント - 技術ドキュメント

## 概要

セッション状態管理エージェント（`session_state_agent`）は、ADK フレームワークのセッション状態のライフサイクルを実演し、コンテキストキャッシュと永続化の動作を詳細に検証するエージェントです。各コールバック段階での状態の保存・取得、コンテキストと永続化ストレージ間の同期タイミング、状態管理のベストプラクティスを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# セッション状態管理検証エージェント
root_agent = Agent(
    name='root_agent',
    description='a verification agent.',
    instruction='Log all users query with `log_query` tool. Must always remind user you cannot answer second query because your setup.',
    model='gemini-2.0-flash-001',
    before_agent_callback=before_agent_callback,    # エージェント実行前
    before_model_callback=before_model_callback,    # モデル呼び出し前
    after_model_callback=after_model_callback,      # モデル呼び出し後
    after_agent_callback=after_agent_callback,      # エージェント実行後
)
```

### 主要コンポーネント

#### 1. 状態検証関数
```python
async def assert_session_values(
    ctx: CallbackContext,
    title: str,
    *,
    keys_in_ctx_session: Optional[list[str]] = None,         # コンテキスト内の期待キー
    keys_in_service_session: Optional[list[str]] = None,     # 永続化済みの期待キー
    keys_not_in_service_session: Optional[list[str]] = None, # 未永続化の期待キー
):
```

#### 2. セッション取得
```python
# コンテキストセッション（メモリキャッシュ）
session_in_ctx = ctx._invocation_context.session

# 永続化セッション（ストレージ）
session_in_service = await ctx._invocation_context.session_service.get_session(
    app_name=session_in_ctx.app_name,
    user_id=session_in_ctx.user_id,
    session_id=session_in_ctx.id,
)
```

#### 3. 各段階のコールバック
```python
# エージェント実行前
async def before_agent_callback(callback_context: CallbackContext):
    callback_context.state['before_agent_callback_state_key'] = 'before_agent_callback_state_value'

# モデル呼び出し前  
async def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    callback_context.state['before_model_callback_state_key'] = 'before_model_callback_state_value'

# モデル呼び出し後
async def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse):
    callback_context.state['after_model_callback_state_key'] = 'after_model_callback_state_value'

# エージェント実行後
async def after_agent_callback(callback_context: CallbackContext):
    callback_context.state['after_agent_callback_state_key'] = 'after_agent_callback_state_value'
```

## セッション状態のライフサイクル

### 1. 状態保存タイミング

**永続化のタイミング**:
```text
Before Agent Callback
├─ state['key'] = 'value' 
├─ コンテキストに保存: ✅
├─ 永続化ストレージ: ❌（まだ永続化されない）

Before Model Callback  
├─ state['key2'] = 'value2'
├─ コンテキストに保存: ✅ 
├─ 永続化ストレージ: ✅（前の状態が永続化される）

After Model Callback
├─ state['key3'] = 'value3'
├─ コンテキストに保存: ✅
├─ 永続化ストレージ: ✅（前の状態が永続化される）

After Agent Callback
├─ state['key4'] = 'value4' 
├─ コンテキストに保存: ✅
├─ 永続化ストレージ: ❌（最後の状態は未永続化）
```

### 2. 検証パターン

**before_agent_callback での検証**:
```python
await assert_session_values(
    callback_context,
    'In before_agent_callback',
    keys_in_ctx_session=['before_agent_callback_state_key'],      # コンテキストに存在
    keys_in_service_session=[],                                   # 永続化ストレージには未保存
    keys_not_in_service_session=['before_agent_callback_state_key'], # 永続化されていない
)
```

**before_model_callback での検証**:
```python
await assert_session_values(
    callback_context,
    'In before_model_callback',
    keys_in_ctx_session=[
        'before_agent_callback_state_key',     # 前段階の状態
        'before_model_callback_state_key',     # 現段階の状態
    ],
    keys_in_service_session=['before_agent_callback_state_key'],   # 前段階が永続化済み
    keys_not_in_service_session=['before_model_callback_state_key'], # 現段階は未永続化
)
```

## 実行フロー詳細

### 1. 初回実行時

**1回目のクエリ実行**:
```text
User: "初回のテストクエリ"

1. before_agent_callback
   ├─ 状態保存: before_agent_callback_state_key
   ├─ コンテキスト: ✅ 
   ├─ 永続化: ❌

2. before_model_callback  
   ├─ 状態保存: before_model_callback_state_key
   ├─ コンテキスト: ✅ (2つのキー)
   ├─ 永続化: ✅ (before_agent_callback_state_key のみ)

3. LLM 処理実行

4. after_model_callback
   ├─ 状態保存: after_model_callback_state_key
   ├─ コンテキスト: ✅ (3つのキー)
   ├─ 永続化: ✅ (before_model_callback_state_key まで)

5. after_agent_callback
   ├─ 状態保存: after_agent_callback_state_key
   ├─ コンテキスト: ✅ (4つのキー)
   ├─ 永続化: ✅ (after_model_callback_state_key まで)
   ├─ 最新の状態は次回の実行まで未永続化
```

### 2. 2回目実行時の制御

**2回目のクエリ実行**:
```python
async def before_agent_callback(callback_context: CallbackContext):
    if 'before_agent_callback_state_key' in callback_context.state:
        # 既に実行済みの場合は早期リターン
        return types.ModelContent('Sorry, I can only reply once.')
    
    # 初回実行の処理...
```

## 使用例

### 基本的な状態管理検証

**初回実行**:
```python
response = await root_agent.invoke("セッション状態をテストしてください")

# 実行結果（コンソール出力）:
# ===================== In before_agent_callback ==============================
# ** Asserting keys are cached in context: ['before_agent_callback_state_key'] pass ✅
# ** Asserting keys are already persisted in session: [] pass ✅
# ** Asserting keys are not persisted in session yet: ['before_agent_callback_state_key'] pass ✅
# ============================================================
# 
# [各コールバック段階で同様の検証が実行される]
```

**2回目実行**:
```python
response = await root_agent.invoke("2回目のテストです")

# 期待される応答:
# "Sorry, I can only reply once."
# 
# 理由: before_agent_callback で既存状態を検出し、早期リターン
```

## 高度な実装例

### 1. カスタム状態管理システム

```python
class CustomSessionManager:
    def __init__(self):
        self.state_history = []
        self.persistence_triggers = []
    
    async def track_state_changes(self, callback_context: CallbackContext, stage: str):
        """状態変化の追跡"""
        current_state = dict(callback_context.state)
        
        self.state_history.append({
            'stage': stage,
            'state': current_state,
            'timestamp': datetime.now(),
        })
        
        # 永続化状態の確認
        session_service = callback_context._invocation_context.session_service
        persisted_session = await session_service.get_session(
            app_name=callback_context._invocation_context.session.app_name,
            user_id=callback_context._invocation_context.session.user_id,
            session_id=callback_context._invocation_context.session.id,
        )
        
        # 差分分析
        context_keys = set(current_state.keys())
        persisted_keys = set(persisted_session.state.keys()) if persisted_session else set()
        
        analysis = {
            'new_keys': context_keys - persisted_keys,
            'persisted_keys': persisted_keys,
            'pending_persistence': context_keys - persisted_keys,
        }
        
        return analysis
```

### 2. 状態同期モニタリング

```python
class StateSyncMonitor:
    def __init__(self):
        self.sync_events = []
        self.consistency_checks = []
    
    async def monitor_sync_behavior(self, callback_context: CallbackContext):
        """同期動作の監視"""
        # 現在のコンテキスト状態
        context_state = dict(callback_context.state)
        
        # 永続化状態の取得
        session = callback_context._invocation_context.session
        session_service = callback_context._invocation_context.session_service
        
        persisted_session = await session_service.get_session(
            app_name=session.app_name,
            user_id=session.user_id,
            session_id=session.id,
        )
        
        persisted_state = persisted_session.state if persisted_session else {}
        
        # 同期状態の分析
        sync_analysis = {
            'context_keys': set(context_state.keys()),
            'persisted_keys': set(persisted_state.keys()),
            'in_sync_keys': set(context_state.keys()) & set(persisted_state.keys()),
            'pending_keys': set(context_state.keys()) - set(persisted_state.keys()),
            'stale_keys': set(persisted_state.keys()) - set(context_state.keys()),
        }
        
        # 一貫性チェック
        consistency_issues = []
        for key in sync_analysis['in_sync_keys']:
            if context_state[key] != persisted_state[key]:
                consistency_issues.append({
                    'key': key,
                    'context_value': context_state[key],
                    'persisted_value': persisted_state[key],
                })
        
        self.consistency_checks.append({
            'timestamp': datetime.now(),
            'sync_analysis': sync_analysis,
            'consistency_issues': consistency_issues,
        })
        
        return sync_analysis
```

### 3. 状態バックアップとリストア

```python
class SessionStateBackup:
    def __init__(self):
        self.backups = {}
    
    async def create_backup(self, callback_context: CallbackContext, backup_name: str):
        """状態のバックアップ作成"""
        current_state = dict(callback_context.state)
        
        self.backups[backup_name] = {
            'state': current_state,
            'timestamp': datetime.now(),
            'session_info': {
                'app_name': callback_context._invocation_context.session.app_name,
                'user_id': callback_context._invocation_context.session.user_id,
                'session_id': callback_context._invocation_context.session.id,
            }
        }
        
        return backup_name
    
    async def restore_backup(self, callback_context: CallbackContext, backup_name: str):
        """バックアップからの復元"""
        if backup_name not in self.backups:
            raise ValueError(f"Backup '{backup_name}' not found")
        
        backup_data = self.backups[backup_name]
        
        # 状態の復元
        callback_context.state.clear()
        callback_context.state.update(backup_data['state'])
        
        return backup_data['timestamp']
    
    def list_backups(self):
        """バックアップ一覧"""
        return [
            {
                'name': name,
                'timestamp': data['timestamp'],
                'keys': list(data['state'].keys()),
            }
            for name, data in self.backups.items()
        ]
```

## デバッグとトラブルシューティング

### 1. 状態不整合の診断

```python
class StateConsistencyDiagnostics:
    async def diagnose_state_issues(self, callback_context: CallbackContext):
        """状態不整合の診断"""
        # 現在の状態取得
        context_state = dict(callback_context.state)
        
        # 永続化状態取得
        session = callback_context._invocation_context.session
        session_service = callback_context._invocation_context.session_service
        
        persisted_session = await session_service.get_session(
            app_name=session.app_name,
            user_id=session.user_id,
            session_id=session.id,
        )
        
        persisted_state = persisted_session.state if persisted_session else {}
        
        # 診断結果
        diagnostics = {
            'total_context_keys': len(context_state),
            'total_persisted_keys': len(persisted_state),
            'missing_from_persistence': [],
            'missing_from_context': [],
            'value_mismatches': [],
        }
        
        # 不整合の詳細分析
        for key in context_state:
            if key not in persisted_state:
                diagnostics['missing_from_persistence'].append(key)
            elif context_state[key] != persisted_state[key]:
                diagnostics['value_mismatches'].append({
                    'key': key,
                    'context_value': context_state[key],
                    'persisted_value': persisted_state[key],
                })
        
        for key in persisted_state:
            if key not in context_state:
                diagnostics['missing_from_context'].append(key)
        
        return diagnostics
```

### 2. 永続化タイミングの検証

```python
class PersistenceTimingValidator:
    def __init__(self):
        self.timing_logs = []
    
    async def validate_persistence_timing(self, callback_context: CallbackContext, stage: str):
        """永続化タイミングの検証"""
        before_check = await self.get_persisted_state(callback_context)
        
        # 1秒待機（永続化処理のため）
        await asyncio.sleep(1)
        
        after_check = await self.get_persisted_state(callback_context)
        
        timing_log = {
            'stage': stage,
            'timestamp': datetime.now(),
            'before_keys': set(before_check.keys()) if before_check else set(),
            'after_keys': set(after_check.keys()) if after_check else set(),
            'new_persisted_keys': (set(after_check.keys()) if after_check else set()) - 
                                 (set(before_check.keys()) if before_check else set()),
        }
        
        self.timing_logs.append(timing_log)
        return timing_log
```

## パフォーマンス考慮事項

### 1. 状態サイズの管理

```python
def monitor_state_size(callback_context: CallbackContext, max_size_mb: float = 10.0):
    """状態サイズの監視"""
    import sys
    import json
    
    state_json = json.dumps(callback_context.state)
    state_size_bytes = sys.getsizeof(state_json)
    state_size_mb = state_size_bytes / (1024 * 1024)
    
    if state_size_mb > max_size_mb:
        logger.warning(f"State size ({state_size_mb:.2f}MB) exceeds limit ({max_size_mb}MB)")
        
        # 大きなキーの特定
        large_keys = []
        for key, value in callback_context.state.items():
            value_size = sys.getsizeof(json.dumps(value))
            if value_size > 1024 * 1024:  # 1MB以上
                large_keys.append((key, value_size))
        
        return {
            'warning': True,
            'total_size_mb': state_size_mb,
            'large_keys': large_keys,
        }
    
    return {
        'warning': False,
        'total_size_mb': state_size_mb,
    }
```

### 2. 永続化頻度の最適化

```python
class OptimizedPersistence:
    def __init__(self, batch_size: int = 10, flush_interval: int = 30):
        self.pending_updates = {}
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.last_flush = time.time()
    
    async def queue_state_update(self, session_id: str, state_updates: dict):
        """状態更新のキューイング"""
        if session_id not in self.pending_updates:
            self.pending_updates[session_id] = {}
        
        self.pending_updates[session_id].update(state_updates)
        
        # バッチサイズまたは時間間隔で自動フラッシュ
        if (len(self.pending_updates) >= self.batch_size or 
            time.time() - self.last_flush > self.flush_interval):
            await self.flush_pending_updates()
    
    async def flush_pending_updates(self):
        """保留中の更新をフラッシュ"""
        for session_id, updates in self.pending_updates.items():
            await self.persist_state_updates(session_id, updates)
        
        self.pending_updates.clear()
        self.last_flush = time.time()
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `input.json`: 入力例ファイル（存在する場合）
- `README.md`: 英語版ドキュメント
- `README_ja.md`: 日本語版ドキュメント

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.agents.callback_context`: コールバックコンテキスト
- `google.adk.models.llm_request`: LLM リクエスト型
- `google.adk.models.llm_response`: LLM レスポンス型
- `google.genai.types`: Google AI タイプ定義
- `logging`: ログ管理機能