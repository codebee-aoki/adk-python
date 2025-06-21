# ADKでollamaモデルを使用する

## モデルの選択

agentがツールに依存している場合は、[ollamaウェブサイト](https://ollama.com/search?c=tools)からツールサポート付きのモデルを選択してください。

信頼性の高い結果を得るために、ツールサポート付きの適切なサイズのモデルを使用することをお勧めします。

モデルのツールサポートは、次のコマンドで確認できます：

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

capabilitiesの下に`tools`がリストされているはずです。

また、モデルが使用しているテンプレートを確認し、必要に応じて調整することもできます。

```bash
ollama show --modelfile llama3.1 > model_file_to_modify
```

その後、次のコマンドでモデルを作成できます：

```bash
ollama create llama3.1-modified -f model_file_to_modify
```

## ollama_chatプロバイダーの使用

私たちのLiteLlmラッパーを使用して、ollamaモデルでagentを作成できます。

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**`ollama`の代わりにプロバイダー`ollama_chat`を設定することが重要です。`ollama`を使用すると、無限のツール呼び出しループや以前のコンテキストの無視などの予期しない動作が発生します。**

生成時にlitellm内で`api_base`を提供することができますが、v1.65.5の時点で、litellmライブラリは完了後に環境変数に依存して他のAPIを呼び出しています。そのため、現時点では環境変数`OLLAMA_API_BASE`をollamaサーバーを指すように設定することをお勧めします。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

## openaiプロバイダーの使用

代わりに、プロバイダー名として`openai`を使用することもできます。ただし、これには`OLLAMA_API_BASE`の代わりに`OPENAI_API_BASE=http://localhost:11434/v1`と`OPENAI_API_KEY=anything`環境変数を設定する必要があります。**api baseの最後に`/v1`が付いていることに注意してください。**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

## デバッグ

インポートの直後にagentコードに以下を追加することで、ollamaサーバーに送信されたリクエストを確認できます。

```py
import litellm
litellm._turn_on_debug()
```

次のような行を探してください：

```bash
quest Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```