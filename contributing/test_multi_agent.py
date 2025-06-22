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
Multi-agent構造のテスト
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types
from samples.wikipedia_person_assistant.agent import coordinator, greeter, wikipedia_person_assistant


async def test_individual_agents():
    """各エージェントの個別テスト"""
    print("=== Multi-agent構造テスト ===")
    print("各エージェントの個別動作確認")
    print("=" * 60)
    
    # 1. Greeter単体テスト
    print("【1. Greeter単体テスト】")
    print("入力: 'こんにちは'")
    print("-" * 30)
    
    runner1 = InMemoryRunner(agent=greeter, app_name='greeter_test')
    session1 = await runner1.session_service.create_session(app_name='greeter_test', user_id='test1')
    content1 = types.Content(role="user", parts=[types.Part(text="こんにちは")])
    
    async for event in runner1.run_async(session_id=session1.id, user_id='test1', new_message=content1):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}] {part.text[:150]}...")
                    break
    
    print("\n" + "=" * 60)
    
    # 2. WikipediaPersonAssistant単体テスト
    print("【2. WikipediaPersonAssistant単体テスト】")
    print("入力: '夏目漱石について教えて'")
    print("-" * 30)
    
    runner2 = InMemoryRunner(agent=wikipedia_person_assistant, app_name='wiki_test')
    session2 = await runner2.session_service.create_session(app_name='wiki_test', user_id='test2')
    content2 = types.Content(role="user", parts=[types.Part(text="夏目漱石について教えて")])
    
    async for event in runner2.run_async(session_id=session2.id, user_id='test2', new_message=content2):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}] {part.text[:150]}...")
                    break
    
    print("\n" + "=" * 60)
    
    # 3. Coordinator統合テスト
    print("【3. Coordinator統合テスト】")
    test_cases = [
        ("挨拶", "こんにちは", "Greeter期待"),
        ("人物名", "夏目漱石について教えて", "WikipediaPersonAssistant期待"),
        ("人物カテゴリ", "明治時代の作家について", "WikipediaPersonAssistant期待"),
    ]
    
    for name, query, expectation in test_cases:
        print(f"\n【{name}】入力: '{query}' ({expectation})")
        print("-" * 30)
        
        runner3 = InMemoryRunner(agent=coordinator, app_name=f'coord_test_{name}')
        session3 = await runner3.session_service.create_session(app_name=f'coord_test_{name}', user_id='test3')
        content3 = types.Content(role="user", parts=[types.Part(text=query)])
        
        event_count = 0
        async for event in runner3.run_async(session_id=session3.id, user_id='test3', new_message=content3):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        event_count += 1
                        print(f"[イベント {event_count}] {event.author}")
                        print(f"{part.text[:100]}...")
                        if event_count >= 2:  # 最大2イベントで停止
                            break
                if event_count >= 2:
                    break


async def test_coordinator_routing():
    """Coordinatorの転送ロジック詳細テスト"""
    print("\n" + "=" * 60)
    print("【Coordinator転送ロジック詳細テスト】")
    
    test_queries = [
        "こんにちは",  # Greeter期待
        "ありがとう",  # Greeter期待  
        "何ができますか？",  # Greeter期待
        "夏目漱石について教えて",  # WikipediaPersonAssistant期待
        "江戸時代の画家について知りたい",  # WikipediaPersonAssistant期待
        "現代音楽で有名な人について",  # WikipediaPersonAssistant期待
    ]
    
    for query in test_queries:
        print(f"\n入力: '{query}'")
        print("-" * 30)
        
        runner = InMemoryRunner(agent=coordinator, app_name='routing_test')
        session = await runner.session_service.create_session(app_name='routing_test', user_id='route_test')
        content = types.Content(role="user", parts=[types.Part(text=query)])
        
        first_agent = None
        async for event in runner.run_async(session_id=session.id, user_id='route_test', new_message=content):
            if event.content and event.content.parts and event.content.parts[0].text:
                if first_agent is None:
                    first_agent = event.author
                    print(f"→ 転送先: {event.author}")
                break


if __name__ == "__main__":
    asyncio.run(test_individual_agents())
    asyncio.run(test_coordinator_routing())