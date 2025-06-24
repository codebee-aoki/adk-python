# エージェント構造図の生成手順

## 概要
Wikipedia人物アシスタントのマルチエージェント構造図を、Draw.ioファイルから画像形式で出力する手順です。

## 方法1: Draw.io Webアプリを使用（推奨）

### 手順
1. **Draw.ioファイルを開く**
   - https://app.diagrams.net/ にアクセス
   - `agent_architecture.drawio` ファイルをアップロード

2. **画像として出力**
   - メニューから `File` → `Export as` → `PNG` を選択
   - 設定:
     - `Zoom`: 200% (高解像度)
     - `Border Width`: 10px (余白)
     - `Transparent Background`: Off
     - `Include a copy of my diagram`: Off
   - `Export` をクリック

3. **ファイル保存**
   - `agent_architecture.png` として保存
   - ハンズオンガイドの `images/` ディレクトリに配置

## 方法2: Draw.io Desktop アプリを使用

### インストール
```bash
# macOS の場合
brew install --cask drawio

# または公式サイトからダウンロード
# https://github.com/jgraph/drawio-desktop/releases
```

### 手順
1. Draw.io デスクトップアプリで `agent_architecture.drawio` を開く
2. `File` → `Export as` → `PNG` を選択
3. 解像度とオプションを設定して出力

## 方法3: コマンドライン（draw.io CLI）

### インストール
```bash
npm install -g @drawio/drawio-cli
```

### 実行
```bash
# PNGとして出力
drawio -x -f png -s 2 agent_architecture.drawio

# SVGとして出力  
drawio -x -f svg agent_architecture.drawio
```

## 出力される図の内容

### 構造図の要素
- **ユーザー**: 質問の起点
- **Coordinator**: 質問分析と振り分け
- **判定ロジック**: 人物関連かどうかの分岐
- **Greeter**: 挨拶・一般質問対応
- **WikipediaPersonAssistant**: 人物検索専門
- **MCP Tools**: Wikipedia検索ツール
- **学習ポイント**: 教育的価値の説明

### 視覚的要素
- **カラーコーディング**: 各エージェントの役割別色分け
- **フロー矢印**: データの流れと処理順序
- **入力例**: 実際の質問パターン
- **出力例**: 各エージェントの応答サンプル

## ハンズオンガイドでの使用

生成された `agent_architecture.png` は、ハンズオンガイドの最初のセクションで表示され:

1. **全体像の理解**: マルチエージェント構造の概観
2. **学習目標の明確化**: 何を学ぶかの視覚的説明  
3. **実習の動機付け**: 実際に動作するシステムの提示

この図により、参加者は実習前にシステム全体を理解し、各ステップの意味を把握できます。