# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Wikipedia人物アシスタント - メイン実行ファイル

このサンプルは、ADKのマルチエージェント機能を使用して、
ユーザーの挨拶から人物検索まで幅広く対応するアシスタントです。

実行方法:
  python contributing/samples/wikipedia_person_assistant/main.py

または:
  cd contributing/samples/wikipedia_person_assistant
  python main.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import root_agent


async def run_interactive_session():
    """対話型セッションを実行"""
    print("=" * 60)
    print("🌟 Wikipedia人物アシスタント 🌟")
    print("=" * 60)
    print("マルチエージェント構造のデモンストレーション")
    print()
    print("このアシスタントは以下の構成で動作します：")
    print("- Coordinator: 質問を分析して適切なエージェントに転送")
    print("- Greeter: 挨拶や一般的な質問に対応")
    print("- WikipediaPersonAssistant: 人物検索と詳細情報提供")
    print()
    print("試してみてください：")
    print("- 「こんにちは」（Greeterエージェントへ）")
    print("- 「夏目漱石について教えて」（WikipediaPersonAssistantエージェントへ）")
    print("- 「江戸時代の画家について知りたい」（WikipediaPersonAssistantエージェントへ）")
    print()
    print("終了するには 'quit' または 'exit' と入力してください。")
    print("=" * 60)
    
    # ランナーとセッションを初期化
    app_name = 'wikipedia_person_assistant'
    user_id = 'interactive_user'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    session = await runner.session_service.create_session(
        app_name=app_name, 
        user_id=user_id
    )
    
    while True:
        try:
            # ユーザー入力を取得
            user_input = input("\n💬 あなた: ").strip()
            
            # 終了コマンドをチェック
            if user_input.lower() in ['quit', 'exit', '終了', 'q']:
                print("\n👋 お疲れ様でした！またお会いしましょう。")
                break
            
            if not user_input:
                print("質問を入力してください。")
                continue
            
            print(f"\n🤖 処理中...")
            
            # ユーザーメッセージを作成
            content = types.Content(
                role="user", 
                parts=[types.Part(text=user_input)]
            )
            
            # エージェントを実行
            response_text = ""
            current_agent = None
            
            async for event in runner.run_async(
                session_id=session.id, 
                user_id=user_id, 
                new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            if current_agent != event.author:
                                current_agent = event.author
                                print(f"\n📋 [{current_agent}]")
                            response_text += part.text
            
            # 最終応答を表示
            if response_text:
                print(response_text)
            else:
                print("申し訳ございません、応答を生成できませんでした。")
                
        except KeyboardInterrupt:
            print("\n\n👋 お疲れ様でした！")
            break
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            print("もう一度お試しください。")


async def run_demo():
    """デモンストレーション実行"""
    print("=" * 60)
    print("🎯 マルチエージェント動作デモ")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        ("挨拶テスト", "こんにちは", "Greeter"),
        ("システム質問", "何ができますか？", "Greeter"), 
        ("具体的人物", "夏目漱石について教えて", "WikipediaPersonAssistant"),
        ("人物カテゴリ", "江戸時代の画家について知りたい", "WikipediaPersonAssistant"),
    ]
    
    # ランナーとセッションを初期化
    app_name = 'wikipedia_demo'
    user_id = 'demo_user'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    session = await runner.session_service.create_session(
        app_name=app_name, 
        user_id=user_id
    )
    
    for i, (test_name, query, expected_agent) in enumerate(test_cases, 1):
        print(f"\n【テスト {i}】{test_name}")
        print(f"入力: '{query}'")
        print(f"期待エージェント: {expected_agent}")
        print("-" * 40)
        
        content = types.Content(
            role="user", 
            parts=[types.Part(text=query)]
        )
        
        actual_agent = None
        response_preview = ""
        
        async for event in runner.run_async(
            session_id=session.id, 
            user_id=user_id, 
            new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        if actual_agent is None:
                            actual_agent = event.author
                            print(f"✅ 実際の転送先: {actual_agent}")
                        
                        if len(response_preview) < 100:
                            response_preview += part.text
        
        # 結果表示
        if response_preview:
            preview = response_preview[:100] + "..." if len(response_preview) > 100 else response_preview
            print(f"応答プレビュー: {preview}")
        
        # 転送先の検証
        if expected_agent in actual_agent:
            print("🎉 転送先が正しいです！")
        else:
            print(f"⚠️  転送先が期待と異なります（期待: {expected_agent}, 実際: {actual_agent}）")
    
    print("\n" + "=" * 60)
    print("🎯 デモが完了しました！")
    print("対話形式で試すには --interactive オプションを使用してください。")
    print("=" * 60)


def main():
    """メイン関数"""
    # API Key確認
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY環境変数が設定されていません。")
        print("貢献ディレクトリの.envファイルにAPI Keyを設定してください。")
        sys.exit(1)
    
    # コマンドライン引数をチェック
    if len(sys.argv) > 1 and sys.argv[1] in ['--interactive', '-i']:
        # 対話モード
        asyncio.run(run_interactive_session())
    else:
        # デモモード
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()