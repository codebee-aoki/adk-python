# 構造化出力エージェント - 技術ドキュメント

## 概要

構造化出力エージェント（`fields_output_schema`）は、Pydantic モデルを使用してエージェントの出力を構造化するデモンストレーションを提供します。天気データを例に、定義されたスキーマに従った一貫性のある出力形式を実現し、API レスポンスや下流システムとの統合を容易にします。

## 技術仕様

### アーキテクチャ

```python
# 構造化出力対応エージェント
root_agent = Agent(
    name='root_agent',
    model='gemini-2.0-flash',
    instruction="...",
    output_schema=WeahterData,      # 出力スキーマの定義
    output_key='weather_data',       # 出力キー
)
```

### 出力スキーマ定義

#### Pydantic モデル
```python
from pydantic import BaseModel

class WeahterData(BaseModel):
    temperature: str    # 温度（文字列形式）
    humidity: str       # 湿度（文字列形式） 
    wind_speed: str     # 風速（文字列形式）
```

**注意**: クラス名の `WeahterData` は意図的なタイポ（Weather → Weahter）

### データソース

#### 1. San Jose の天気データ
```python
# システム指示に埋め込まれたデータ
* temperature: 26 C
* humidity: 20%
* wind_speed: 29 mph
```

#### 2. Cupertino の天気データ
```python
# システム指示に埋め込まれたデータ  
* temperature: 16 C
* humidity: 10%
* wind_speed: 13 mph
```

## 実行フロー

### 1. 入力処理
- ユーザーからの天気情報リクエスト
- 地域指定（San Jose または Cupertino）

### 2. データ検索
- システム指示内の事前定義データから該当地域の情報を検索
- データが存在しない場合は「わからない」と応答

### 3. 構造化出力生成
```python
# 出力例（San Jose の場合）
{
    "weather_data": {
        "temperature": "26 C",
        "humidity": "20%", 
        "wind_speed": "29 mph"
    }
}
```

## 使用例

### 基本的な使用方法

**San Jose の天気情報取得**:
```python
response = await root_agent.invoke("San Jose の天気を教えてください")

# 期待される出力
{
    "weather_data": {
        "temperature": "26 C",
        "humidity": "20%",
        "wind_speed": "29 mph"
    }
}
```

**Cupertino の天気情報取得**:
```python
response = await root_agent.invoke("Cupertino の気象情報は？")

# 期待される出力  
{
    "weather_data": {
        "temperature": "16 C",
        "humidity": "10%",
        "wind_speed": "13 mph"
    }
}
```

**未対応地域への対応**:
```python
response = await root_agent.invoke("Tokyo の天気は？")

# 期待される出力
{
    "weather_data": {
        "temperature": "わからない",
        "humidity": "わからない", 
        "wind_speed": "わからない"
    }
}
```

## 構造化出力の利点

### 1. 一貫性の保証
- すべての応答が同じ構造を持つ
- フィールドの欠損を防止
- 型の整合性を確保

### 2. API 統合の簡素化
```python
# 構造化された出力の利用
weather_response = await agent.invoke(query)
temperature = weather_response['weather_data']['temperature']
humidity = weather_response['weather_data']['humidity']
wind_speed = weather_response['weather_data']['wind_speed']
```

### 3. 下流システムとの互換性
```python
# データベース挿入
weather_record = WeahterData(**response['weather_data'])
database.insert(weather_record)

# JSON API レスポンス
return jsonify(response['weather_data'])
```

## 高度な実装例

### 1. 複雑なスキーマ定義

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DetailedWeatherData(BaseModel):
    location: str = Field(description="観測地点")
    timestamp: datetime = Field(description="観測時刻")
    temperature: float = Field(description="気温（摂氏）")
    humidity: int = Field(ge=0, le=100, description="湿度（パーセント）")
    wind_speed: float = Field(ge=0, description="風速（m/s）")
    conditions: List[str] = Field(description="気象条件")
    forecast: Optional[str] = Field(description="予報")
```

### 2. バリデーション付きスキーマ

```python
from pydantic import BaseModel, validator

class ValidatedWeatherData(BaseModel):
    temperature: str
    humidity: str
    wind_speed: str
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if 'C' not in v and 'F' not in v:
            raise ValueError('Temperature must include unit (C or F)')
        return v
    
    @validator('humidity')  
    def validate_humidity(cls, v):
        if '%' not in v:
            raise ValueError('Humidity must include % symbol')
        return v
```

### 3. 動的スキーマ選択

```python
# 地域に応じたスキーマの選択
def get_weather_schema(region: str):
    if region in ['US', 'Canada']:
        return USWeatherData
    elif region in ['Europe', 'Asia']:
        return MetricWeatherData
    else:
        return StandardWeatherData

agent = Agent(
    output_schema=get_weather_schema(user_region),
    # ...
)
```

## 実践的な応用例

### 1. 気象 API サービス
```python
class WeatherAPI:
    def __init__(self):
        self.agent = Agent(
            model='gemini-2.0-flash',
            output_schema=WeahterData,
            output_key='weather_data'
        )
    
    async def get_weather(self, location: str) -> WeahterData:
        response = await self.agent.invoke(f"{location}の天気")
        return WeahterData(**response['weather_data'])
```

### 2. データ集約システム
```python
class WeatherAggregator:
    async def collect_regional_data(self, locations: List[str]):
        weather_data = []
        for location in locations:
            data = await weather_agent.invoke(f"{location}の天気")
            weather_data.append(data['weather_data'])
        return weather_data
```

### 3. 監視・アラートシステム
```python
class WeatherMonitor:
    async def check_conditions(self, location: str):
        weather = await weather_agent.invoke(f"{location}の天気")
        data = weather['weather_data']
        
        # 構造化データによる条件判定
        if self.parse_wind_speed(data['wind_speed']) > 50:
            await self.send_alert(f"Strong winds in {location}")
```

## 技術的制約と考慮事項

### 1. データ型の制約
- 現在の実装では全フィールドが `str` 型
- 数値計算が必要な場合は型変換が必要

### 2. 静的データソース
- データはシステム指示に静的に埋め込み
- 動的データソースとの統合には追加実装が必要

### 3. エラーハンドリング
- 未対応地域の場合の標準的な応答
- スキーマ違反時の処理

## 拡張可能性

### 1. 外部データソース統合
```python
# 気象API との統合例
async def get_weather_data(location: str):
    external_data = await weather_api.fetch(location)
    return format_to_schema(external_data)
```

### 2. 多言語対応
```python
class MultiLanguageWeatherData(BaseModel):
    temperature: str
    humidity: str  
    wind_speed: str
    language: str = "ja"
```

### 3. 単位変換機能
```python
def convert_units(data: WeahterData, target_unit: str):
    # 温度や風速の単位変換
    pass
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- Pydantic モデル定義

## 依存関係

- `google.adk`: ADK フレームワーク
- `pydantic`: データ検証とシリアライゼーション
- Python 標準ライブラリ