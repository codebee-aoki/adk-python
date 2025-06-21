# ライブ双方向ストリーミングエージェント - 技術ドキュメント

## 概要

ライブ双方向ストリーミングエージェント（`live_bidi_streaming_agent`）は、Gemini 2.0 Flash Live モデルを使用してリアルタイム双方向通信を実現するエージェントです。サイコロ転がしと素数判定のデモンストレーションを通じて、ストリーミング中のツール呼び出し、状態管理、リアルタイム応答などの高度な機能を学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# ライブストリーミング対応エージェント
root_agent = Agent(
    model='gemini-2.0-flash-live-preview-04-09',  # Vertex AI プロジェクト用
    # model='gemini-2.0-flash-live-001',          # AI Studio キー用
    name='hello_world_agent',
    description='hello world agent that can roll a dice of 8 sides and check prime numbers.',
    instruction="...",  # リアルタイム処理指示
    tools=[roll_die, check_prime],
    generate_content_config=types.GenerateContentConfig(...),
)
```

### 主要コンポーネント

#### 1. ライブストリーミングモデル
```python
# Vertex AI プロジェクト用（推奨）
model='gemini-2.0-flash-live-preview-04-09'

# AI Studio キー用（代替）
model='gemini-2.0-flash-live-001'
```

#### 2. リアルタイム対応ツール

**サイコロ転がしツール**:
```python
def roll_die(sides: int, tool_context: ToolContext) -> int:
    """リアルタイムサイコロ転がし"""
    result = random.randint(1, sides)
    
    # ストリーミング中の状態管理
    if not 'rolls' in tool_context.state:
        tool_context.state['rolls'] = []
    tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
    
    return result
```

**素数判定ツール（非同期）**:
```python
async def check_prime(nums: list[int]) -> str:
    """非同期素数判定（ストリーミング対応）"""
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
    
    return (
        'No prime numbers found.'
        if not primes
        else f"{', '.join(str(num) for num in primes)} are prime numbers."
    )
```

### ストリーミング設定

#### 安全設定
```python
generate_content_config=types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.OFF,  # サイコロ転がしの誤検知回避
        ),
    ]
)
```

## ストリーミング実行フロー

### 1. 双方向ストリーミング開始

**接続確立**:
```python
# ストリーミングセッション開始
stream = await root_agent.start_streaming()

# リアルタイム通信チャネル確立
# - ユーザー → エージェント（音声/テキスト入力）
# - エージェント → ユーザー（リアルタイム応答）
```

### 2. リアルタイム処理フロー

**単一ツール実行**:
```text
ユーザー入力（リアルタイム）: "6面サイコロを転がして"

ストリーミング処理:
1. 音声/テキスト認識（リアルタイム）
2. 意図理解とツール選択
3. roll_die(6) 実行
4. 結果のストリーミング配信
5. 状態の即座更新

リアルタイム応答: "6面サイコロの結果は...4です！"
```

**複合ツール実行**:
```text
ユーザー入力: "サイコロを転がして素数判定して"

ストリーミング処理:
1. roll_die(6) 実行 → "結果は7です"（即座配信）
2. check_prime([7]) 実行
3. "7は素数です！"（即座配信）

特徴: 各ステップの結果を待機せずにストリーミング
```

### 3. 並列処理と状態同期

**複数ツールの並列実行**:
```text
ユーザー: "4面、6面、8面のサイコロを同時に転がして"

並列ストリーミング:
- roll_die(4) || roll_die(6) || roll_die(8)
- 結果が出た順にリアルタイム配信
- "4面: 3", "6面: 5", "8面: 7"
- 状態の一貫性を保持
```

## 高度なストリーミング機能

### 1. 中断・再開機能

```python
# ストリーミング中断
await stream.pause()

# 処理再開
await stream.resume()

# 緊急停止
await stream.stop()
```

### 2. 状態の永続化

```python
# ストリーミング中の状態保存
stream_state = {
    'rolls': tool_context.state.get('rolls', []),
    'session_id': stream.session_id,
    'timestamp': time.time(),
}

# 状態復元
await stream.restore_state(stream_state)
```

### 3. エラー回復

```python
try:
    result = await stream.process_input(user_input)
except StreamingError as e:
    # ストリーミングエラーの回復
    await stream.recover_from_error(e)
    # 処理続行
```

## 実践的な使用例

### 基本的なストリーミング

```python
# ストリーミングセッション開始
async def start_live_session():
    stream = await root_agent.start_streaming()
    
    # ユーザー入力の処理
    async for user_input in stream.listen():
        # リアルタイム応答
        response = await stream.process(user_input)
        # 即座に配信
        await stream.send(response)
```

### 音声対応ストリーミング

```python
# 音声入力対応
async def voice_streaming():
    stream = await root_agent.start_streaming(
        input_mode='voice',      # 音声入力
        output_mode='voice',     # 音声出力
        language='ja-JP',        # 日本語対応
    )
    
    async for voice_input in stream.listen_voice():
        # 音声認識 → テキスト処理 → 音声合成
        response = await stream.process_voice(voice_input)
        await stream.speak(response)
```

### マルチユーザーストリーミング

```python
# 複数ユーザーの同時接続
class MultiUserStreamingManager:
    def __init__(self):
        self.active_streams = {}
    
    async def add_user(self, user_id: str):
        stream = await root_agent.start_streaming()
        self.active_streams[user_id] = stream
        return stream
    
    async def broadcast_to_all(self, message: str):
        for stream in self.active_streams.values():
            await stream.send(message)
```

## 高度な応用例

### 1. ゲーミングチャットボット

```python
class GamingChatBot:
    async def handle_game_commands(self, stream):
        async for input in stream.listen():
            if "dice" in input.lower():
                # リアルタイムサイコロ転がし
                result = await self.roll_dice_with_animation(stream)
                await stream.send_with_effects(f"🎲 {result}")
            
            elif "stats" in input.lower():
                # リアルタイム統計表示
                stats = self.get_player_stats()
                await stream.send_live_chart(stats)
```

### 2. 教育アシスタント

```python
class EducationalAssistant:
    async def math_tutoring_session(self, stream):
        async for question in stream.listen():
            if "prime" in question:
                # 段階的解説
                await stream.send("素数を確認しますね...")
                result = await check_prime([7])
                await stream.send(f"結果: {result}")
                await stream.send("素数の定義は...")
```

### 3. データ分析ダッシュボード

```python
class LiveDataDashboard:
    async def real_time_analysis(self, stream):
        while stream.is_active():
            # リアルタイムデータ更新
            data = await self.fetch_live_data()
            analysis = await self.analyze_data(data)
            
            # ストリーミング配信
            await stream.send_chart_update(analysis)
            await asyncio.sleep(1)  # 1秒間隔更新
```

## パフォーマンス最適化

### 1. レイテンシ最適化

```python
# 低レイテンシ設定
stream_config = {
    'buffer_size': 512,      # 小さなバッファ
    'processing_timeout': 100,  # 100ms タイムアウト
    'parallel_processing': True,  # 並列処理有効
}

stream = await root_agent.start_streaming(**stream_config)
```

### 2. 帯域幅管理

```python
# 帯域幅制御
bandwidth_config = {
    'max_concurrent_streams': 10,   # 最大同時ストリーム数
    'compression': 'gzip',          # データ圧縮
    'quality': 'adaptive',          # 適応品質調整
}
```

### 3. メモリ管理

```python
# メモリ効率化
memory_config = {
    'state_cleanup_interval': 60,   # 60秒間隔でクリーンアップ
    'max_history_size': 1000,       # 履歴最大サイズ
    'garbage_collection': True,     # 自動ガベージコレクション
}
```

## トラブルシューティング

### 1. 接続問題
```python
# 接続リトライ機能
async def robust_streaming():
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            stream = await root_agent.start_streaming()
            return stream
        except ConnectionError:
            retry_count += 1
            await asyncio.sleep(2 ** retry_count)  # 指数バックオフ
```

### 2. レイテンシ問題
```python
# レイテンシ監視
async def monitor_latency(stream):
    async for input in stream.listen():
        start_time = time.time()
        response = await stream.process(input)
        latency = time.time() - start_time
        
        if latency > 0.5:  # 500ms 超過時
            logger.warning(f"High latency detected: {latency:.2f}s")
```

### 3. モデル互換性
```python
# モデル自動選択
def select_streaming_model():
    if is_vertex_ai_available():
        return 'gemini-2.0-flash-live-preview-04-09'
    else:
        return 'gemini-2.0-flash-live-001'

model = select_streaming_model()
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `readme.md`: 英語版ドキュメント
- `readme_ja.md`: 日本語版ドキュメント

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.tools.tool_context`: ツールコンテキスト
- `google.genai.types`: Google AI タイプ定義
- `random`: 乱数生成（サイコロ機能）
- **Gemini 2.0 Flash Live モデル**: ライブストリーミング機能