# セッション状態の永続化をデモンストレーションするサンプルAgent

## セッション状態のライフサイクル

contextオブジェクトを使用して状態を割り当てた後（例：
`tool_context.state['log_query_var'] = 'log_query_var_value'`）：

* その状態は後のコールバックで使用できるようになります。
* 結果のイベントがランナーによって処理され、セッションに追加されると、状態もセッションに永続化されます。

このサンプルagentは、上記の動作を実証するためのものです。

## agentの実行

以下のコマンドを実行してください：

```bash
$ adk run contributing/samples/session_state_agent --replay contributing/samples/session_state_agent/input.json
```

以下の出力が表示されるはずです：

```bash
[user]: hello world!
===================== In before_agent_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: [] pass ✅
** Asserting keys are not persisted in session yet: ['before_agent_callback_state_key'] pass ✅
============================================================
===================== In before_model_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key', 'before_model_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: ['before_agent_callback_state_key'] pass ✅
** Asserting keys are not persisted in session yet: ['before_model_callback_state_key'] pass ✅
============================================================
===================== In after_model_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key', 'before_model_callback_state_key', 'after_model_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: ['before_agent_callback_state_key'] pass ✅
** Asserting keys are not persisted in session yet: ['before_model_callback_state_key', 'after_model_callback_state_key'] pass ✅
============================================================
[root_agent]: Hello! How can I help you verify something today?

===================== In after_agent_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key', 'before_model_callback_state_key', 'after_model_callback_state_key', 'after_agent_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: ['before_agent_callback_state_key', 'before_model_callback_state_key', 'after_model_callback_state_key'] pass ✅
** Asserting keys are not persisted in session yet: ['after_agent_callback_state_key'] pass ✅
============================================================
```

## 詳細な説明

経験則として、セッション状態を読み書きする際、ユーザーはcontextオブジェクト
（`tool_context`、`callback_context`、または`readonly_context`）を介して書き込んだ後に、状態が利用可能であると仮定すべきです。

### 現在の動作

状態を永続化する現在の動作は以下の通りです：

* `before_agent_callback`の場合：状態のdeltaは、すべてのコールバックが処理された後に永続化されます。
* `before_model_callback`の場合：状態のdeltaは最終的なLlmResponse、
  つまり`after_model_callback`が処理された後に永続化されます。
* `after_model_callback`の場合：状態のdeltaはLlmResponseのイベントと一緒に永続化されます。
* `after_agent_callback`の場合：状態のdeltaは、すべてのコールバックが処理された後に永続化されます。

**注意**：現在の動作は実装の詳細と見なされ、後で変更される可能性があります。**これに依存しないでください**。