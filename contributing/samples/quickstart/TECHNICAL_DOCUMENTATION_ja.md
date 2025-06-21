# quickstart - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`quickstart` エージェントは、ADK の最も簡潔なサンプル実装として設計されています。天気予報と時刻取得の基本的な機能を通じて、カスタムツール開発の基本パターンを学習するためのエントリーポイントとして機能します。

### 主要機能
- **天気取得機能**: 指定された都市の天気情報を取得
- **時刻取得機能**: 指定された都市の現在時刻を表示
- **エラーハンドリング**: 未対応都市への適切な応答
- **構造化レスポンス**: 統一されたレスポンス形式

### 対象ユースケース
- ADK 初心者向けチュートリアル
- シンプルなカスタムツール開発の学習
- エラーハンドリングパターンの理解
- 構造化データレスポンスの実装例

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (天気/時刻の質問)
[weather_time_agent] 
    ↓ (ツール呼び出し)
[カスタムツール群]
    ├── get_weather() - 天気情報取得 (モック)
    └── get_current_time() - 時刻取得 (実時刻)
    ↓ (構造化レスポンス)
[統一レスポンス形式]
    ├── status: "success" | "error"
    ├── report: "実際のデータ" (成功時)
    └── error_message: "エラー詳細" (失敗時)
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス)
- **天気ツール**: `get_weather` - モックデータ提供
- **時刻ツール**: `get_current_time` - 実際の時刻計算
- **エラーハンドリング**: 統一されたエラーレスポンス
- **レスポンス構造**: 辞書ベースの構造化データ

### データフロー
1. ユーザーが天気または時刻情報を要求
2. エージェントが適切なツールを選択・呼び出し
3. ツールが処理を実行し、構造化レスポンスを返却
4. エージェントがレスポンスを解釈してユーザーに回答

### 依存関係
```python
# 標準ライブラリ
import datetime  # 時刻処理用
from zoneinfo import ZoneInfo  # タイムゾーン処理用

# ADK コンポーネント
from google.adk.agents import Agent
```

## 3. コード詳細解説

### 3.1 天気取得ツール

```python
def get_weather(city: str) -> dict:
  """Retrieves the current weather report for a specified city.

  Args:
      city (str): The name of the city for which to retrieve the weather report.

  Returns:
      dict: status and result or error msg.
  """
  if city.lower() == "new york":
    return {
        "status": "success",
        "report": (
            "The weather in New York is sunny with a temperature of 25 degrees"
            " Celsius (77 degrees Fahrenheit)."
        ),
    }
  else:
    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }
```

**重要な実装ポイント:**
- **モック実装**: 実際のAPIではなく、固定データを返却
- **統一レスポンス**: `status` フィールドで成功/失敗を明示
- **大小文字無視**: `city.lower()` で入力の柔軟性を提供
- **詳細なエラーメッセージ**: ユーザーに分かりやすいエラー内容

### 3.2 時刻取得ツール

```python
def get_current_time(city: str) -> dict:
  """Returns the current time in a specified city.

  Args:
      city (str): The name of the city for which to retrieve the current time.

  Returns:
      dict: status and result or error msg.
  """
  import datetime
  from zoneinfo import ZoneInfo

  if city.lower() == "new york":
    tz_identifier = "America/New_York"
  else:
    return {
        "status": "error",
        "error_message": (
            f"Sorry, I don't have timezone information for {city}."
        ),
    }

  tz = ZoneInfo(tz_identifier)
  now = datetime.datetime.now(tz)
  report = (
      f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
  )
  return {"status": "success", "report": report}
```

**重要な実装ポイント:**
- **実時刻計算**: `datetime.datetime.now()` で実際の時刻を取得
- **タイムゾーン対応**: `ZoneInfo` でタイムゾーン変換
- **関数内インポート**: 必要な時点でライブラリをインポート
- **フォーマット指定**: 読みやすい時刻形式で出力

### 3.3 エージェント設定

```python
root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "I can answer your questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)
```

**設計の特徴:**
- **シンプルな構成**: 最小限の設定項目
- **明確な責務**: 天気と時刻の2つの機能に特化
- **直感的な命名**: 機能が分かりやすいエージェント名

## 4. 設定・環境構築

### 4.1 必要な環境変数
```bash
# .env ファイルまたは環境変数
# Google GenAI API の設定が必要
GOOGLE_API_KEY=your_api_key
```

### 4.2 依存関係とインストール
```bash
# 基本依存関係は ADK に含まれる
pip install google-adk

# Python 3.9+ (zoneinfo サポートのため)
python --version  # 3.9以上を確認
```

### 4.3 実行方法
```bash
# CLI での実行
adk run contributing/samples/quickstart

# Web UI での実行  
adk web contributing/samples/quickstart
```

### 4.4 タイムゾーンサポート
```python
# Python 3.9+ の zoneinfo を使用
# 古いバージョンの場合は pytz をインストール
pip install pytz  # Python < 3.9 の場合

# 代替実装 (pytz 使用)
import pytz
tz = pytz.timezone("America/New_York")
now = datetime.datetime.now(tz)
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### 天気情報の取得
```
ユーザー: "What's the weather like in New York?"
エージェント: [get_weather ツールを呼び出し] 
"The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit)."
```

#### 時刻情報の取得
```
ユーザー: "What time is it in New York?"
エージェント: [get_current_time ツールを呼び出し]
"The current time in New York is 2025-01-15 14:30:45 EST-0500"
```

#### エラーケース
```
ユーザー: "What's the weather in Tokyo?"
エージェント: [get_weather ツールを呼び出し]
"Sorry, weather information for 'Tokyo' is not available."
```

### 5.2 カスタマイズポイント

#### 対応都市の拡張
```python
def get_weather(city: str) -> dict:
    """Enhanced weather function with multiple cities"""
    weather_data = {
        "new york": {
            "temperature": 25,
            "condition": "sunny",
            "humidity": 60
        },
        "tokyo": {
            "temperature": 18,
            "condition": "cloudy", 
            "humidity": 75
        },
        "london": {
            "temperature": 12,
            "condition": "rainy",
            "humidity": 85
        }
    }
    
    city_key = city.lower()
    if city_key in weather_data:
        data = weather_data[city_key]
        return {
            "status": "success",
            "report": f"The weather in {city} is {data['condition']} with a temperature of {data['temperature']}°C and humidity of {data['humidity']}%."
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available."
        }
```

#### 実際のAPIとの統合
```python
import requests

def get_weather_api(city: str) -> dict:
    """Real weather API integration"""
    try:
        api_key = os.getenv("WEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        return {
            "status": "success",
            "report": f"The weather in {city} is {data['weather'][0]['description']} with a temperature of {data['main']['temp']}°C."
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve weather data: {str(e)}"
        }
```

#### 追加情報の提供
```python
def get_city_info(city: str) -> dict:
    """Get comprehensive city information"""
    city_data = {
        "new york": {
            "country": "USA",
            "population": "8.3 million",
            "timezone": "America/New_York",
            "founded": "1624"
        }
    }
    
    city_key = city.lower()
    if city_key in city_data:
        data = city_data[city_key]
        return {
            "status": "success",
            "report": f"{city} is located in {data['country']}, has a population of {data['population']}, and was founded in {data['founded']}."
        }
    else:
        return {
            "status": "error", 
            "error_message": f"City information for '{city}' is not available."
        }

# エージェントに追加
root_agent = Agent(
    tools=[get_weather, get_current_time, get_city_info],
    # ...
)
```

### 5.3 マルチエージェント統合
```python
# 専門エージェントの作成
weather_agent = Agent(
    name="WeatherSpecialist",
    tools=[get_weather],
    instruction="I specialize in weather information."
)

time_agent = Agent(
    name="TimeSpecialist", 
    tools=[get_current_time],
    instruction="I specialize in time information."
)

# 統合エージェント
coordinator_agent = Agent(
    name="CityInfoCoordinator",
    sub_agents=[weather_agent, time_agent],
    instruction="I coordinate weather and time information requests."
)
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "ModuleNotFoundError: No module named 'zoneinfo'"
**原因**: Python 3.8 以前のバージョンを使用
**解決法**: Python 3.9+ にアップグレードまたは pytz を使用
```bash
# Python アップグレード
python --version  # 3.9+ を確認

# または pytz を使用
pip install pytz

# コード修正
import pytz
tz = pytz.timezone("America/New_York")
```

#### エラー: "KeyError: 'report'"
**原因**: レスポンス形式の不整合
**解決法**: エラー時の適切なハンドリング
```python
def safe_get_weather(city: str) -> dict:
    try:
        result = get_weather(city)
        if result["status"] == "success":
            return result["report"]
        else:
            return result["error_message"]
    except KeyError as e:
        return f"Response format error: {str(e)}"
```

### 6.2 デバッグ方法

#### レスポンス内容の確認
```python
def debug_weather(city: str) -> dict:
    result = get_weather(city)
    print(f"Weather result for {city}: {result}")
    return result
```

#### ログ出力の追加
```python
import logging

def get_weather_with_logging(city: str) -> dict:
    logging.info(f"Getting weather for city: {city}")
    result = get_weather(city)
    logging.info(f"Weather result: {result}")
    return result
```

### 6.3 パフォーマンス考慮事項

- **関数内インポート**: 頻繁に呼び出される場合はモジュールレベルでインポート
- **レスポンスキャッシュ**: 同じ都市の重複リクエスト対策
- **タイムアウト設定**: 外部API統合時の応答時間制限

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### シンプルなツール設計
- 単一責務の原則に従った機能分割
- 統一されたレスポンス形式
- 明確なエラーハンドリング

#### 構造化レスポンス
```python
# 良い例: 統一されたレスポンス形式
def consistent_tool(input_data: str) -> dict:
    try:
        result = process_data(input_data)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# 悪い例: 不整合なレスポンス
def inconsistent_tool(input_data: str):
    if input_data == "good":
        return "Success"  # 文字列
    else:
        return {"error": "Failed"}  # 辞書
```

#### エラーハンドリングパターン
- ユーザーフレンドリーなエラーメッセージ
- 原因を特定できる詳細な情報
- グレースフルデグラデーション

### 7.2 他のプロジェクトへの応用

#### 情報取得エージェント
```python
def get_stock_price(symbol: str) -> dict:
    """Stock price information agent"""
    # 実装ロジック
    pass

def get_news_headlines(topic: str) -> dict:
    """News headlines agent""" 
    # 実装ロジック
    pass
```

#### サービス統合エージェント  
```python
def send_email(to: str, subject: str, body: str) -> dict:
    """Email sending agent"""
    # 実装ロジック
    pass

def create_calendar_event(title: str, date: str) -> dict:
    """Calendar event creation agent"""
    # 実装ロジック
    pass
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **統一レスポンス**: 全ツールで一貫したレスポンス形式を使用
- **明確な docstring**: 引数、戻り値、動作を詳細に記述
- **エラーハンドリング**: 予期される全てのエラーケースに対応
- **テストフレンドリー**: モックデータを活用した実装

#### 注意点
- **ハードコーディング**: 本番環境では外部設定を使用
- **エラー情報**: 機密情報を含むエラーメッセージに注意
- **レスポンス形式**: ツール間での整合性を保持
- **入力検証**: ユーザー入力の適切な検証とサニタイゼーション

この quickstart エージェントは、ADK におけるシンプルなカスタムツール開発の基本パターンを学ぶのに最適な例です。統一されたレスポンス形式とエラーハンドリングの実装は、より複雑なプロジェクトでも応用できる重要なパターンです。