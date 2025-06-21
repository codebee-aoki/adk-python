# 長時間実行ツールを使用したAgent

この例では、長時間実行ツール（`ask_for_approval`）を使用するagentを示します。

## 長時間実行ツールの主要なフロー

1.  **初回呼び出し**: agentが長時間実行ツール（例：`ask_for_approval`）を呼び出します。
2.  **初回ツールレスポンス**: ツールは即座に初期レスポンスを返します。通常は「保留中」のステータスとリクエストを追跡する方法（例：`ticket-id`）を示します。これは`types.FunctionResponse`としてagentに送り返されます（通常はランナーによって内部的に処理され、agentの次のターンに影響を与えます）。
3.  **Agentの確認**: agentはこの初期レスポンスを処理し、通常はユーザーに保留中のステータスについて通知します。
4.  **外部プロセス/更新**: 長時間実行タスクが外部で進行します（例：人間がリクエストを承認する）。
5.  **❗️重要なステップ: 更新されたツールレスポンスの提供❗️**:
    * 外部プロセスが完了または更新されたら、アプリケーションは新しい`types.FunctionResponse`を**必ず**構築する必要があります。
    * このレスポンスは、長時間実行ツールへの元の`FunctionCall`と**同じ`id`と`name`**を使用する必要があります。
    * この`types.FunctionResponse`内の`response`フィールドには、*更新されたデータ*（例：`{'status': 'approved', ...}`）を含める必要があります。
    * この`types.FunctionResponse`を`role="user"`で新しいメッセージの一部としてagentに送り返します。

    ```python
    # 例: 外部承認後
    updated_tool_output_data = {
        "status": "approved",
        "ticket-id": ticket_id, # 元の呼び出しから
        # ... その他の関連する更新データ
    }

    updated_function_response_part = types.Part(
        function_response=types.FunctionResponse(
            id=long_running_function_call.id,   # 元の呼び出しID
            name=long_running_function_call.name, # 元の呼び出し名
            response=updated_tool_output_data,
        )
    )

    # これをagentに送り返す
    await runner.run_async(
        # ... session_id, user_id ...
        new_message=types.Content(
            parts=[updated_function_response_part], role="user"
        ),
    )
    ```
6.  **Agentが更新に基づいて行動**: agentは`types.FunctionResponse`を含むこのメッセージを受信し、その指示に基づいて次のステップを進めます（例：`reimburse`のような別のツールを呼び出す）。

**なぜこれが重要なのか？** agentは、長時間実行タスクが終了したか、その状態が変更されたことを理解するために、この後続の`types.FunctionResponse`（特定の`Part`を含む`role="user"`のメッセージで提供される）を受信することに依存しています。これがないと、agentは保留中のタスクの結果を認識できません。