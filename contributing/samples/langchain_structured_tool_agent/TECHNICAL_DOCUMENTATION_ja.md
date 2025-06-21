# LangChain 構造化ツール統合エージェント - 技術ドキュメント

## 概要

LangChain 構造化ツール統合エージェント（`langchain_structured_tool_agent`）は、LangChain エコシステムの `StructuredTool` を ADK フレームワークで使用する方法を実演するエージェントです。Pydantic によるスキーマ検証、型安全性、LangChain との相互運用性を活用し、既存の LangChain ツールを ADK エージェントで活用できます。

## 技術仕様

### アーキテクチャ

```python
# LangChain ツール統合エージェント
root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="test_app",
    description="A helpful assistant for user questions.",
    instruction="You are a helpful assistant for user questions, you have access to a tool that adds two numbers.",
    tools=[LangchainTool(tool=test_langchain_tool)],  # LangChain ツールのラップ
)
```

### 主要コンポーネント

#### 1. ツール関数定義
```python
def add(x, y) -> int:
    """二つの数値を加算"""
    return x + y
```

#### 2. Pydantic スキーマ
```python
from pydantic import BaseModel

class AddSchema(BaseModel):
    x: int  # 第一引数（整数）
    y: int  # 第二引数（整数）
```

#### 3. LangChain StructuredTool
```python
from langchain_core.tools.structured import StructuredTool

test_langchain_tool = StructuredTool.from_function(
    add,                           # 実行関数
    name="add",                    # ツール名
    description="Adds two numbers", # ツール説明
    args_schema=AddSchema,         # 引数スキーマ
)
```

#### 4. ADK ツールラッパー
```python
from google.adk.tools.langchain_tool import LangchainTool

# LangChain ツールを ADK で使用可能にする
LangchainTool(tool=test_langchain_tool)
```

## 実行フロー

### 1. ツールの登録と初期化

**LangChain ツールの作成**:
```python
# 1. 関数定義
def add(x, y) -> int:
    return x + y

# 2. スキーマ定義  
class AddSchema(BaseModel):
    x: int
    y: int

# 3. StructuredTool 作成
structured_tool = StructuredTool.from_function(
    func=add,
    name="add",
    description="Adds two numbers",
    args_schema=AddSchema,
)

# 4. ADK ツールとしてラップ
adk_tool = LangchainTool(tool=structured_tool)
```

### 2. エージェント実行フロー

**数値加算の実行**:
```python
user_input = "15 + 27 を計算してください"

# エージェントの処理:
# 1. ユーザーリクエストの解析
# 2. add ツールの呼び出し判定
# 3. パラメータ抽出: x=15, y=27
# 4. スキーマ検証（AddSchema）
# 5. add(15, 27) 実行
# 6. 結果 42 を返却
```

## 使用例

### 基本的な使用方法

**シンプルな計算**:
```python
response = await root_agent.invoke("5 と 8 を足してください")

# 実行フロー:
# 1. LangchainTool が add ツールを呼び出し
# 2. AddSchema による引数検証: {x: 5, y: 8}
# 3. add(5, 8) 実行
# 4. 結果: 13

# 期待される応答:
# "5と8を足した結果は13です。"
```

**複数回の計算**:
```python
response = await root_agent.invoke("10 + 20 と 30 + 40 を計算してください")

# エージェントは以下のように処理:
# 1. add(10, 20) → 30
# 2. add(30, 40) → 70  
# 3. 両方の結果を応答に含める
```

### 複雑な数学的処理

**段階的計算**:
```python
query = """
以下の計算を順番に行ってください：
1. 25 + 75
2. その結果に 50 を加算
3. 最終結果を教えてください
"""

response = await root_agent.invoke(query)

# 処理手順:
# 1. add(25, 75) → 100
# 2. add(100, 50) → 150
# 3. "最終結果は150です"
```

## 高度な実装例

### 1. 複雑なスキーマ定義

```python
from pydantic import BaseModel, Field
from typing import Optional

class AdvancedMathSchema(BaseModel):
    operation: str = Field(description="数学演算の種類")
    operands: list[float] = Field(description="演算対象の数値リスト")
    precision: Optional[int] = Field(default=2, description="小数点以下の桁数")

def advanced_math(operation: str, operands: list[float], precision: int = 2) -> float:
    """高度な数学演算"""
    if operation == "sum":
        result = sum(operands)
    elif operation == "product":
        result = 1
        for num in operands:
            result *= num
    elif operation == "average":
        result = sum(operands) / len(operands)
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    
    return round(result, precision)

advanced_tool = StructuredTool.from_function(
    advanced_math,
    name="advanced_math",
    description="Performs advanced mathematical operations",
    args_schema=AdvancedMathSchema,
)
```

### 2. 多機能ツールセット

```python
# 複数の LangChain ツール統合
class StringSchema(BaseModel):
    text: str
    operation: str  # "upper", "lower", "reverse"

def string_processor(text: str, operation: str) -> str:
    operations = {
        "upper": text.upper,
        "lower": text.lower,
        "reverse": lambda: text[::-1]
    }
    return operations[operation]()

string_tool = StructuredTool.from_function(
    string_processor,
    name="string_processor", 
    description="Processes strings with various operations",
    args_schema=StringSchema,
)

# 複数ツールを持つエージェント
multi_tool_agent = Agent(
    model="gemini-2.0-flash-001",
    name="multi_tool_agent",
    tools=[
        LangchainTool(tool=test_langchain_tool),  # 数値加算
        LangchainTool(tool=string_tool),          # 文字列処理
        LangchainTool(tool=advanced_tool),        # 高度な数学
    ],
)
```

### 3. エラーハンドリング付きツール

```python
class SafeMathSchema(BaseModel):
    x: float
    y: float
    operation: str = Field(regex="^(add|subtract|multiply|divide)$")

def safe_math(x: float, y: float, operation: str) -> dict:
    """エラーハンドリング付き数学演算"""
    try:
        if operation == "add":
            result = x + y
        elif operation == "subtract":
            result = x - y
        elif operation == "multiply":
            result = x * y
        elif operation == "divide":
            if y == 0:
                return {"error": "Division by zero is not allowed"}
            result = x / y
        else:
            return {"error": f"Unsupported operation: {operation}"}
        
        return {"result": result, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

safe_math_tool = StructuredTool.from_function(
    safe_math,
    name="safe_math",
    description="Performs safe mathematical operations with error handling",
    args_schema=SafeMathSchema,
)
```

## 実践的な応用例

### 1. データ処理パイプライン

```python
class DataProcessorSchema(BaseModel):
    data: list[dict]
    operation: str
    field: str

def process_data(data: list[dict], operation: str, field: str) -> list[dict]:
    """データ処理ツール"""
    if operation == "filter_positive":
        return [item for item in data if item.get(field, 0) > 0]
    elif operation == "sum_field":
        return [{"total": sum(item.get(field, 0) for item in data)}]
    elif operation == "group_by":
        # グループ化処理
        pass
    return data

data_tool = StructuredTool.from_function(
    process_data,
    name="process_data",
    description="Processes data collections",
    args_schema=DataProcessorSchema,
)
```

### 2. API 統合ツール

```python
class APICallSchema(BaseModel):
    endpoint: str
    method: str = "GET"
    params: Optional[dict] = None
    headers: Optional[dict] = None

async def api_caller(endpoint: str, method: str = "GET", params: dict = None, headers: dict = None):
    """外部 API 呼び出しツール"""
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=method,
            url=endpoint,
            params=params,
            headers=headers
        ) as response:
            return {
                "status": response.status,
                "data": await response.json(),
            }

api_tool = StructuredTool.from_function(
    api_caller,
    name="api_caller",
    description="Makes API calls to external services",
    args_schema=APICallSchema,
)
```

### 3. ファイル処理ツール

```python
class FileProcessorSchema(BaseModel):
    file_path: str
    operation: str  # "read", "count_lines", "get_size"

def file_processor(file_path: str, operation: str):
    """ファイル処理ツール"""
    import os
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    if operation == "read":
        with open(file_path, 'r') as f:
            return {"content": f.read()}
    elif operation == "count_lines":
        with open(file_path, 'r') as f:
            return {"line_count": len(f.readlines())}
    elif operation == "get_size":
        return {"size_bytes": os.path.getsize(file_path)}
    
    return {"error": "Unsupported operation"}

file_tool = StructuredTool.from_function(
    file_processor,
    name="file_processor",
    description="Processes files with various operations",
    args_schema=FileProcessorSchema,
)
```

## 統合のメリット

### 1. 型安全性
- Pydantic による厳密な型チェック
- 実行時の引数検証
- IDE でのタイプヒント支援

### 2. LangChain エコシステムとの互換性
- 既存の LangChain ツールの再利用
- LangChain コミュニティツールの活用
- 段階的な移行が可能

### 3. スキーマドリブン開発
- 明確な API 契約
- 自動的なドキュメント生成
- テスト容易性の向上

## 制約と考慮事項

### 1. パフォーマンス
- スキーマ検証のオーバーヘッド
- シリアライゼーション/デシリアライゼーション

### 2. 依存関係
- LangChain と ADK の両方が必要
- バージョン互換性の管理

### 3. エラーハンドリング
- 複数レイヤーでのエラー処理
- スキーマ検証エラーの適切な処理

## 関連ファイル

- `agent.py`: メインエージェント実装

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.tools.langchain_tool`: LangChain ツール統合
- `langchain_core.tools.structured`: LangChain 構造化ツール
- `pydantic`: データ検証とスキーマ定義