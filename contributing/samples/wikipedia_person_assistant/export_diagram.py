#!/usr/bin/env python3
"""
Draw.io図をPNG形式でエクスポートするスクリプト
drawio-mcp-serverを使用してWikipedia人物アシスタントの構造図を画像化
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# MCPクライアントのインポート
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ MCPライブラリがインストールされていません。")
    print("以下のコマンドでインストールしてください:")
    print("pip install mcp")
    sys.exit(1)

async def export_diagram_to_png():
    """Draw.io図をPNG形式でエクスポート"""
    
    # ファイルパスの設定
    current_dir = Path(__file__).parent
    drawio_file = current_dir / "agent_architecture.drawio"
    output_file = current_dir / "agent_architecture.png"
    
    if not drawio_file.exists():
        print(f"❌ Draw.ioファイルが見つかりません: {drawio_file}")
        return False
    
    try:
        # drawio-mcp-serverに接続
        server_params = StdioServerParameters(
            command="drawio-mcp-server",
            args=[]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # サーバーの初期化
                await session.initialize()
                
                # 利用可能なツールを確認
                tools = await session.list_tools()
                print(f"✅ 利用可能なツール: {[tool.name for tool in tools.tools]}")
                
                # Draw.ioファイルを読み込み
                with open(drawio_file, 'r', encoding='utf-8') as f:
                    diagram_content = f.read()
                
                # 図をPNG形式でエクスポート
                export_args = {
                    "diagram": diagram_content,
                    "format": "png",
                    "pageIndex": 0,  # 最初のページを出力
                    "scale": 2.0,    # 高解像度で出力
                    "transparent": False,
                    "border": 10     # 余白を追加
                }
                
                # エクスポートツールを実行
                result = await session.call_tool("export_diagram", export_args)
                
                if result.content and len(result.content) > 0:
                    # Base64データをデコードして保存
                    import base64
                    
                    # 結果からbase64データを取得
                    image_data = None
                    for content in result.content:
                        if hasattr(content, 'text'):
                            # JSONレスポンスの場合
                            try:
                                response = json.loads(content.text)
                                if 'data' in response:
                                    image_data = response['data']
                                elif 'image' in response:
                                    image_data = response['image']
                            except json.JSONDecodeError:
                                # 直接base64データの場合
                                image_data = content.text
                        elif hasattr(content, 'data'):
                            # バイナリデータの場合
                            image_data = base64.b64encode(content.data).decode('utf-8')
                    
                    if image_data:
                        # Base64データをデコードして保存
                        png_data = base64.b64decode(image_data)
                        with open(output_file, 'wb') as f:
                            f.write(png_data)
                        
                        print(f"✅ 図を正常にエクスポートしました: {output_file}")
                        print(f"📁 ファイルサイズ: {len(png_data):,} bytes")
                        return True
                    else:
                        print("❌ エクスポート結果からbase64データを取得できませんでした")
                        print(f"レスポンス: {result}")
                        return False
                else:
                    print("❌ エクスポートツールから結果が返されませんでした")
                    return False
                    
    except FileNotFoundError:
        print("❌ drawio-mcp-serverが見つかりません。")
        print("以下のコマンドでインストールしてください:")
        print("npm install -g drawio-mcp-server")
        return False
    except Exception as e:
        print(f"❌ エクスポート中にエラーが発生しました: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_connection():
    """drawio-mcp-serverとの接続をテスト"""
    try:
        server_params = StdioServerParameters(
            command="drawio-mcp-server",
            args=["--help"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print(f"✅ drawio-mcp-serverに正常に接続しました")
                print(f"利用可能なツール: {[tool.name for tool in tools.tools]}")
                return True
                
    except FileNotFoundError:
        print("❌ drawio-mcp-serverが見つかりません")
        return False
    except Exception as e:
        print(f"❌ 接続テストでエラー: {e}")
        return False

def main():
    """メイン実行関数"""
    print("🎨 Wikipedia人物アシスタント構造図のエクスポート")
    print("=" * 60)
    
    # MCPサーバーとの接続をテスト
    print("1. drawio-mcp-serverとの接続をテスト中...")
    if not asyncio.run(test_mcp_connection()):
        print("\n❌ drawio-mcp-serverに接続できませんでした。")
        print("以下のコマンドでインストールしてください:")
        print("npm install -g drawio-mcp-server")
        sys.exit(1)
    
    # 図をエクスポート
    print("\n2. Draw.io図をPNG形式でエクスポート中...")
    success = asyncio.run(export_diagram_to_png())
    
    if success:
        print("\n🎉 エクスポートが完了しました！")
        print("agent_architecture.png ファイルをハンズオンガイドで使用できます。")
    else:
        print("\n❌ エクスポートに失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    main()