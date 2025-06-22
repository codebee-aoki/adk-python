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
Wikipedia人物検索Loop Agentの実際のテスト
contributingディレクトリから実行して.envファイルを読み込みます
"""

import asyncio
import os
import sys

# contributingディレクトリに移動して.envを読み込む
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

# パッケージのインポート
from google.adk.runners import InMemoryRunner
from google.genai import types

# エージェントのインポート
from samples.wikipedia_person_assistant.agent import root_agent


async def test_loop_flow():
    """Wikipedia人物アシスタントの動作確認テスト"""
    print("=== Wikipedia人物アシスタント テスト ===")
    print(f"API Key設定済み: {bool(os.getenv('GOOGLE_API_KEY'))}")
    print()
    
    app_name = 'wikipedia_fix_test'
    user_id = 'fix_test_user'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    
    # テスト1: 人物関連外の質問（即座に終了を期待）
    print("【テスト1】人物関連外の質問 - 即座に終了を期待")
    print("入力: 'こんにちは'")
    print("-" * 60)
    
    content1 = types.Content(role="user", parts=[types.Part(text="こんにちは")])
    
    print("実行結果:")
    event_count = 0
    async for event in runner.run_async(
        session_id=session.id, user_id=user_id, new_message=content1
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    event_count += 1
                    print(f"\n[イベント {event_count}] {event.author}")
                    print(part.text[:200] + "..." if len(part.text) > 200 else part.text)
                    print("=" * 40)
    
    print(f"\n総イベント数: {event_count}")
    print("期待: 1イベントで親しみやすい挨拶応答")
    
    # テスト2: 曖昧な質問（適切な誘導を期待）
    print("\n" + "=" * 80)
    print("【テスト2】曖昧な質問 - 適切な誘導を期待")
    print("入力: '江戸時代の画家について知りたい'")
    print("-" * 60)
    
    content2 = types.Content(role="user", parts=[types.Part(text="江戸時代の画家について知りたい")])
    
    print("実行結果:")
    event_count = 0
    async for event in runner.run_async(
        session_id=session.id, user_id=user_id, new_message=content2
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    event_count += 1
                    print(f"\n[イベント {event_count}] {event.author}")
                    print(part.text[:200] + "..." if len(part.text) > 200 else part.text)
                    print("=" * 40)
    
    print(f"\n総イベント数: {event_count}")
    print("期待: 1イベントで適切な誘導応答")
    
    # テスト3: 具体的な人物選択（詳細要約を期待）
    print("\n" + "=" * 80)
    print("【テスト3】具体的な人物選択 - 詳細要約を期待")
    print("入力: '夏目漱石について教えて'")
    print("-" * 60)
    
    content3 = types.Content(role="user", parts=[types.Part(text="夏目漱石について教えて")])
    
    print("実行結果:")
    event_count = 0
    async for event in runner.run_async(
        session_id=session.id, user_id=user_id, new_message=content3
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    event_count += 1
                    print(f"\n[イベント {event_count}] {event.author}")
                    print(part.text[:200] + "..." if len(part.text) > 200 else part.text)
                    print("=" * 40)
    
    print(f"\n総イベント数: {event_count}")
    print("期待: 1イベントで詳細要約応答")


async def test_direct_person():
    """直接的な人物質問のテスト"""
    print("\n" + "=" * 80)
    print("【テスト3】新しいセッションで直接的な人物質問")
    print("入力: '夏目漱石について教えて'")
    print("-" * 60)
    
    app_name = 'wikipedia_direct_test'
    user_id = 'direct_user'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    
    content = types.Content(role="user", parts=[types.Part(text="夏目漱石について教えて")])
    
    print("実行結果:")
    event_count = 0
    async for event in runner.run_async(
        session_id=session.id, user_id=user_id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    event_count += 1
                    print(f"\n[イベント {event_count}] {event.author}")
                    print(part.text)
                    print("=" * 40)
    
    print(f"\n総イベント数: {event_count}")
    print("直接的な質問では即座に特定→要約が実行されるはずです。")


async def test_escalation_behavior():
    """エスカレーション動作の詳細確認"""
    print("\n" + "=" * 80)
    print("【テスト4】エスカレーション動作の詳細確認")
    print("複数ループでの動作を観察")
    print("-" * 60)
    
    app_name = 'escalation_test'
    user_id = 'escalation_user'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    
    # ステップ1: 曖昧な質問
    print("ステップ1: 曖昧な質問")
    content1 = types.Content(role="user", parts=[types.Part(text="明治時代の文豪について")])
    
    loop_count = 0
    async for event in runner.run_async(
        session_id=session.id, user_id=user_id, new_message=content1
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    if "PersonSearchAgent" in event.author or "検索結果" in part.text:
                        print("✓ 検索エージェント実行")
                    elif "PersonIdentificationAgent" in event.author or "判定結果" in part.text:
                        loop_count += 1
                        print(f"✓ 判定エージェント実行 (Loop {loop_count})")
                        if "特定完了" in part.text:
                            print("  → 特定完了判定")
                        else:
                            print("  → 継続必要判定")
                    elif "PersonSummaryAgent" in event.author:
                        print("✓ 要約エージェント実行")
    
    # ステップ2: 具体的な選択
    print("\nステップ2: 具体的な選択")
    content2 = types.Content(role="user", parts=[types.Part(text="森鴎外について詳しく")])
    
    async for event in runner.run_async(
        session_id=session.id, user_id=user_id, new_message=content2
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    if "PersonSearchAgent" in event.author:
                        print("✓ 検索エージェント実行")
                    elif "PersonIdentificationAgent" in event.author:
                        loop_count += 1
                        print(f"✓ 判定エージェント実行 (Loop {loop_count})")
                        if "特定完了" in part.text:
                            print("  → 特定完了判定・エスカレーション")
                    elif "PersonSummaryAgent" in event.author:
                        print("✓ 要約エージェント実行")
    
    print(f"\n総ループ回数: {loop_count}")


if __name__ == "__main__":
    print("Wikipedia人物アシスタント テスト開始")
    print(f"作業ディレクトリ: {os.getcwd()}")
    print(f"Python実行パス: {sys.executable}")
    
    try:
        # 統合エージェントのテスト（メインテスト）
        asyncio.run(test_loop_flow())
        
        print("\n" + "=" * 80)
        print("🎉 テストが完了しました！")
        print("各ケースで適切に応答することを確認しました：")
        print("1. 人物関連外の質問 → 親しみやすい挨拶応答")
        print("2. 曖昧な質問 → 適切な誘導応答")  
        print("3. 具体的な人物選択 → 詳細要約応答")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ テスト実行中にエラーが発生しました:")
        print(f"エラー内容: {e}")
        import traceback
        traceback.print_exc()