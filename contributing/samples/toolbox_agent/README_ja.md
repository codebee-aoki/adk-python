# Toolbox Agent

このagentは、データベースに保存されている情報に基づいてエンドユーザーを支援するために[mcp toolbox for database](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)を使用しています。
このagentを実行するには以下の手順に従ってください

# toolboxのインストール

* 以下のコマンドを実行してください：

```bash
export OS="linux/amd64" # linux/amd64, darwin/arm64, darwin/amd64, windows/amd64のいずれか
curl -O https://storage.googleapis.com/genai-toolbox/v0.5.0/$OS/toolbox
chmod +x toolbox
```

# SQLiteのインストール

* https://sqlite.org/ からsqliteをインストールしてください


# DBの作成（オプション。dbインスタンスは既にフォルダーに添付されています）

* 以下のコマンドを実行してください：

```bash
sqlite3 tool_box.db
```

* 以下のSQLを実行してください：

```sql
CREATE TABLE hotels(
  id            INTEGER NOT NULL PRIMARY KEY,
  name          VARCHAR NOT NULL,
  location      VARCHAR NOT NULL,
  price_tier    VARCHAR NOT NULL,
  checkin_date  DATE    NOT NULL,
  checkout_date DATE    NOT NULL,
  booked        BIT     NOT NULL
);


INSERT INTO hotels(id, name, location, price_tier, checkin_date, checkout_date, booked)
VALUES 
  (1, 'Hilton Basel', 'Basel', 'Luxury', '2024-04-22', '2024-04-20', 0),
  (2, 'Marriott Zurich', 'Zurich', 'Upscale', '2024-04-14', '2024-04-21', 0),
  (3, 'Hyatt Regency Basel', 'Basel', 'Upper Upscale', '2024-04-02', '2024-04-20', 0),
  (4, 'Radisson Blu Lucerne', 'Lucerne', 'Midscale', '2024-04-24', '2024-04-05', 0),
  (5, 'Best Western Bern', 'Bern', 'Upper Midscale', '2024-04-23', '2024-04-01', 0),
  (6, 'InterContinental Geneva', 'Geneva', 'Luxury', '2024-04-23', '2024-04-28', 0),
  (7, 'Sheraton Zurich', 'Zurich', 'Upper Upscale', '2024-04-27', '2024-04-02', 0),
  (8, 'Holiday Inn Basel', 'Basel', 'Upper Midscale', '2024-04-24', '2024-04-09', 0),
  (9, 'Courtyard Zurich', 'Zurich', 'Upscale', '2024-04-03', '2024-04-13', 0),
  (10, 'Comfort Inn Bern', 'Bern', 'Midscale', '2024-04-04', '2024-04-16', 0);
```

# ツール設定の作成

* "tools.yaml"という名前のyamlファイルを作成してください。agentフォルダーでその内容を確認してください。

# toolboxサーバーの起動

* agentフォルダーで以下のコマンドを実行してください

```bash
toolbox --tools-file "tools.yaml"
```

# ADK web UIの起動

# ユーザークエリの送信

* クエリ1: what can you do for me ?
* クエリ2: could you let know the information about "Hilton Basel" hotel ?