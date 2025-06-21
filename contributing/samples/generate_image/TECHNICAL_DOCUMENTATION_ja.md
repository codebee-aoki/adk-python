# 画像生成エージェント - 技術ドキュメント

## 概要

画像生成エージェント（`generate_image`）は、Google の Imagen 3.0 モデルを使用してテキストプロンプトから画像を生成し、アーティファクトとして保存・管理するエージェントです。生成された画像の保存、読み込み、質問応答まで一貫して処理できる包括的な画像処理ソリューションを提供します。

## 技術仕様

### アーキテクチャ

```python
# 画像生成対応エージェント
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description="An agent that generates images and answer questions about the images.",
    instruction="You are an agent whose job is to generate or edit an image based on the user's prompt.",
    tools=[generate_image, load_artifacts],  # 画像生成とアーティファクト管理
)
```

### 主要コンポーネント

#### 1. 画像生成クライアント
```python
from google.genai import Client

# Vertex AI クライアント（画像生成対応）
client = Client()
```

#### 2. 画像生成ツール
```python
async def generate_image(prompt: str, tool_context: 'ToolContext'):
    """テキストプロンプトから画像を生成"""
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',  # Imagen 3.0 モデル
        prompt=prompt,
        config={'number_of_images': 1},   # 生成枚数
    )
```

#### 3. アーティファクト管理
```python
# 生成画像の保存
await tool_context.save_artifact(
    'image.png',  # ファイル名
    types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
)

# 保存済みアーティファクトの読み込み
from google.adk.tools import load_artifacts
```

## 実行フロー

### 1. 画像生成プロセス

**リクエスト処理**:
```python
# プロンプト受信
user_prompt = "美しい夕日の風景"

# Imagen 3.0 への API 呼び出し
response = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt=user_prompt,
    config={'number_of_images': 1},
)
```

**レスポンス処理**:
```python
# 生成結果の確認
if not response.generated_images:
    return {'status': 'failed'}

# 画像データの取得
image_bytes = response.generated_images[0].image.image_bytes
```

### 2. アーティファクト保存

**ファイル保存**:
```python
# PNG形式での保存
await tool_context.save_artifact(
    'image.png',
    types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
)

# 成功レスポンス
return {
    'status': 'success',
    'detail': 'Image generated successfully and stored in artifacts.',
    'filename': 'image.png',
}
```

### 3. 画像の読み込みと分析

**アーティファクトの読み込み**:
```python
# load_artifacts ツールの使用
artifacts = load_artifacts()
# 保存済み画像の一覧と内容を取得
```

## 使用例

### 基本的な画像生成

**シンプルな画像生成**:
```python
response = await root_agent.invoke("猫が遊んでいる画像を生成してください")

# 実行フロー:
# 1. generate_image("猫が遊んでいる画像") を呼び出し
# 2. Imagen 3.0 で画像生成
# 3. image.png として保存
# 4. 成功メッセージを返却
```

**詳細なプロンプト指定**:
```python
prompt = """
美しい日本庭園の風景。桜の花が満開で、
小さな池に鯉が泳いでいる。早朝の柔らかな光が
庭全体を照らしている。写実的なスタイルで。
"""

response = await root_agent.invoke(f"以下のプロンプトで画像を生成: {prompt}")
```

### 画像の確認と質問応答

**生成画像の確認**:
```python
# 画像生成後の質問
response1 = await root_agent.invoke("森の中の小屋の画像を生成してください")
response2 = await root_agent.invoke("生成した画像について説明してください")

# エージェントは load_artifacts を使用して画像を読み込み、
# 画像の内容について質問に回答
```

**複数画像の管理**:
```python
# 複数の画像生成（順次実行）
await root_agent.invoke("山の風景を生成してください")
await root_agent.invoke("海の風景を生成してください")  
await root_agent.invoke("これまでに生成した画像を比較してください")
```

## 高度な機能

### 1. エラーハンドリング

**生成失敗の処理**:
```python
if not response.generated_images:
    return {
        'status': 'failed',
        'error': 'Image generation failed',
        'details': 'No images were generated from the prompt'
    }
```

### 2. カスタムファイル名

**動的ファイル名生成**:
```python
import datetime

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"generated_image_{timestamp}.png"

await tool_context.save_artifact(
    filename,
    types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
)
```

### 3. バッチ画像生成

**複数画像の生成**:
```python
async def generate_multiple_images(prompts: list[str], tool_context: 'ToolContext'):
    results = []
    for i, prompt in enumerate(prompts):
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config={'number_of_images': 1},
        )
        
        if response.generated_images:
            filename = f"image_{i+1}.png"
            await tool_context.save_artifact(
                filename,
                types.Part.from_bytes(
                    data=response.generated_images[0].image.image_bytes,
                    mime_type='image/png'
                ),
            )
            results.append(filename)
    
    return results
```

## 設定とカスタマイズ

### 1. モデル設定

**Imagen 3.0 パラメータ**:
```python
config = {
    'number_of_images': 1,          # 生成枚数
    'aspect_ratio': '1:1',          # アスペクト比
    'safety_filter_level': 'block_some',  # 安全フィルタ
    'person_generation': 'allow_all',     # 人物生成設定
}

response = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt=prompt,
    config=config,
)
```

### 2. 出力形式の変更

**JPEG形式での保存**:
```python
await tool_context.save_artifact(
    'image.jpg',
    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
)
```

**複数形式での保存**:
```python
# PNG と JPEG の両方で保存
await tool_context.save_artifact('image.png', png_part)
await tool_context.save_artifact('image.jpg', jpeg_part)
```

## 実践的な応用例

### 1. コンテンツ制作支援

```python
class ContentCreationAgent:
    async def create_blog_images(self, article_topics: list[str]):
        """ブログ記事用の画像を一括生成"""
        for topic in article_topics:
            prompt = f"ブログ記事用の魅力的な画像: {topic}"
            await self.generate_and_save(prompt, f"{topic}_blog.png")
```

### 2. プロトタイプ作成

```python
class PrototypeAgent:
    async def create_ui_mockups(self, ui_descriptions: list[str]):
        """UI モックアップの生成"""
        for desc in ui_descriptions:
            prompt = f"モダンなWebアプリケーションの{desc}画面"
            await self.generate_and_save(prompt, f"ui_{desc}.png")
```

### 3. 教育コンテンツ生成

```python
class EducationalAgent:
    async def create_learning_materials(self, concepts: list[str]):
        """学習教材用の画像生成"""
        for concept in concepts:
            prompt = f"教育用のわかりやすい{concept}の図解"
            await self.generate_and_save(prompt, f"edu_{concept}.png")
```

## セキュリティと制約

### 1. Vertex AI 要件
```text
**重要**: Vertex AI プロジェクトでのみ画像生成が利用可能
- AI Studio キーでは画像生成不可
- 適切な権限とクォータが必要
```

### 2. プロンプト制約
```python
# 安全フィルタによる制限
# - 暴力的コンテンツ
# - 成人向けコンテンツ  
# - ヘイトスピーチ
# - 著作権侵害の可能性があるコンテンツ
```

### 3. リソース管理
```python
# API クォータ制限
# - 1日あたりの生成枚数制限
# - 同時リクエスト数制限
# - ファイルサイズ制限
```

## トラブルシューティング

### 1. 生成失敗
```python
# 一般的な失敗原因:
# - プロンプトが安全フィルタに抵触
# - API クォータ超過
# - ネットワーク接続問題
# - Vertex AI プロジェクト設定問題
```

### 2. アーティファクト保存失敗
```python
# 保存時のエラー確認
try:
    await tool_context.save_artifact(filename, image_part)
except Exception as e:
    print(f"アーティファクト保存エラー: {e}")
```

### 3. 画像品質の問題
```python
# プロンプト最適化の例
good_prompt = "高品質で詳細な日本の城、晴れた日、プロフェッショナル写真、8K解像度"
bad_prompt = "城"  # 詳細不足
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `sample.session.json`: セッション例（存在する場合）

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.tools`: アーティファクト管理ツール
- `google.genai`: Google AI クライアント
- `google.genai.types`: データ型定義
- Vertex AI プロジェクト: 画像生成 API アクセス