# Agent Development Kit (ADK)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Unit Tests](https://github.com/google/adk-python/actions/workflows/python-unit-tests.yml/badge.svg)](https://github.com/google/adk-python/actions/workflows/python-unit-tests.yml)
[![r/agentdevelopmentkit](https://img.shields.io/badge/Reddit-r%2Fagentdevelopmentkit-FF4500?style=flat&logo=reddit&logoColor=white)](https://www.reddit.com/r/agentdevelopmentkit/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/google/adk-python)

<html>
    <h2 align="center">
      <img src="https://raw.githubusercontent.com/google/adk-python/main/assets/agent-development-kit.png" width="256"/>
    </h2>
    <h3 align="center">
      洗練された AI エージェントを柔軟性と制御性を持って構築、評価、デプロイするためのオープンソースのコードファースト Python ツールキット
    </h3>
    <h3 align="center">
      重要なリンク:
      <a href="https://google.github.io/adk-docs/">ドキュメント</a>, 
      <a href="https://github.com/google/adk-samples">サンプル</a>,
      <a href="https://github.com/google/adk-java">Java ADK</a> &
      <a href="https://github.com/google/adk-web">ADK Web</a>.
    </h3>
</html>

Agent Development Kit (ADK) は、AI エージェントの開発とデプロイのための柔軟でモジュラーなフレームワークです。Gemini と Google エコシステム向けに最適化されていますが、ADK はモデル非依存、デプロイメント非依存であり、他のフレームワークとの互換性を考慮して構築されています。ADK は、エージェント開発をよりソフトウェア開発に近い感覚にし、開発者がシンプルなタスクから複雑なワークフローまでのエージェントアーキテクチャを簡単に作成、デプロイ、オーケストレーションできるように設計されました。


---

## ✨ 主な機能

- **豊富なツールエコシステム**: 事前構築されたツール、カスタム関数、
  OpenAPI 仕様を活用したり、既存のツールを統合してエージェントに多様な
  機能を与え、Google エコシステムとの緊密な統合を実現します。

- **コードファースト開発**: エージェントロジック、ツール、オーケストレーションを
  Python で直接定義し、究極の柔軟性、テスト容易性、バージョン管理を実現します。

- **モジュラーマルチエージェントシステム**: 複数の専門エージェントを柔軟な階層に
  構成することで、スケーラブルなアプリケーションを設計します。

- **どこでもデプロイ**: エージェントを簡単にコンテナ化し、Cloud Run にデプロイしたり、
  Vertex AI Agent Engine でシームレスにスケールできます。

## 🤖 Agent2Agent (A2A) プロトコルと ADK 統合

リモートエージェント間通信のために、ADK は
[A2A プロトコル](https://github.com/google-a2a/A2A/)と統合します。
連携方法については、この[例](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/google_adk)
をご覧ください。

## 🚀 インストール

### 安定版リリース（推奨）

`pip` を使用して ADK の最新安定版をインストールできます：

```bash
pip install google-adk
```

リリースサイクルは週次です。

このバージョンは最新の公式リリースを表しており、ほとんどのユーザーに推奨されます。

### 開発版
バグ修正と新機能は、まず GitHub の main ブランチにマージされます。公式の PyPI リリースにまだ含まれていない変更にアクセスする必要がある場合は、main ブランチから直接インストールできます：

```bash
pip install git+https://github.com/google/adk-python.git@main
```

注意：開発版は最新のコードコミットから直接ビルドされます。最新の修正と機能が含まれていますが、安定版リリースには存在しない実験的な変更やバグが含まれている可能性もあります。主に今後の変更をテストしたり、公式リリース前の重要な修正にアクセスしたりする場合に使用してください。

## 📚 ドキュメンテーション

エージェントの構築、評価、デプロイに関する詳細なガイドについては、
完全なドキュメントをご覧ください：

* **[ドキュメント](https://google.github.io/adk-docs)**

## 🏁 機能ハイライト

### 単一エージェントの定義：

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.0-flash", # または、お好みの Gemini モデル
    instruction="You are a helpful assistant. Answer user questions using Google Search when needed.",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

### マルチエージェントシステムの定義：

コーディネーターエージェント、グリーターエージェント、タスク実行エージェントを含むマルチエージェントシステムを定義します。その後、ADK エンジンとモデルがエージェントを連携させてタスクを達成します。

```python
from google.adk.agents import LlmAgent, BaseAgent

# 個々のエージェントを定義
greeter = LlmAgent(name="greeter", model="gemini-2.0-flash", ...)
task_executor = LlmAgent(name="task_executor", model="gemini-2.0-flash", ...)

# 親エージェントを作成し、sub_agents で子を割り当て
coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash",
    description="I coordinate greetings and tasks.",
    sub_agents=[ # ここで sub_agents を割り当て
        greeter,
        task_executor
    ]
)
```

### 開発 UI

エージェントのテスト、評価、デバッグ、ショーケースに役立つ組み込みの開発 UI。

<img src="https://raw.githubusercontent.com/google/adk-python/main/assets/adk-web-dev-ui-function-call.png"/>

###  エージェントの評価

```bash
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

## 🤝 コントリビューション

コミュニティからの貢献を歓迎します！バグレポート、機能リクエスト、ドキュメントの改善、コードの貢献など、以下をご覧ください：
- [一般的な貢献ガイドラインとフロー](https://google.github.io/adk-docs/contributing-guide/#questions)
- コードを貢献したい場合は、[コード貢献ガイドライン](./CONTRIBUTING.md)をお読みください。

## 📄 ライセンス

このプロジェクトは Apache 2.0 License の下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

---

*Happy Agent Building!*