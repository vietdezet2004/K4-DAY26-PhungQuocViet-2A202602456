"""MCP Client có Authentication — kết nối tới auth_server.py qua HTTP.

Client tạo HTTP client bằng create_mcp_http_client(headers=...) của MCP SDK
(đúng thư viện HTTP mà SDK dùng bên dưới, kèm timeout khuyến nghị). Header
Authorization được gắn vào mọi request HTTP (POST, GET, DELETE) tới server.

Cách chạy (cần auth_server.py đang chạy ở terminal khác):
    cd 03-production
    python auth_server.py            # terminal 1
    python auth_client.py            # terminal 2
"""

from __future__ import annotations

import asyncio

import os

from mcp import ClientSession
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client

SERVER_URL = "http://localhost:8000/mcp"
TOKEN = os.environ.get("MCP_AUTH_TOKEN", "dev-token-abc123")


async def main() -> None:
    print("=== Thử nghiệm 1: Gửi Token hợp lệ ===")
    http_client = create_mcp_http_client(
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    async with http_client:
        async with streamable_http_client(SERVER_URL, http_client=http_client) as (
            read,
            write,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                print("✅ Kết nối thành công! Tools (có auth):")
                for t in tools.tools:
                    print(f"  - {t.name}: {t.description}")

                result = await session.call_tool("get_weather", {"city": "Hanoi"})
                print(f"  -> Kết quả gọi tool: {result.content[0].text}")

    print("\n=== Thử nghiệm 2: Gửi Token sai (Security Check) ===")
    bad_client = create_mcp_http_client(
        headers={"Authorization": "Bearer wrong-token-999"},
    )
    try:
        async with bad_client:
            async with streamable_http_client(SERVER_URL, http_client=bad_client) as (
                read,
                write,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    await session.list_tools()
        print("❌ Lỗi: Token sai nhưng vẫn truy cập được!")
    except Exception as e:
        print(f"🔒 Bảo mật thành công: Request mang token sai đã bị chặn ({type(e).__name__})")


if __name__ == "__main__":
    asyncio.run(main())
