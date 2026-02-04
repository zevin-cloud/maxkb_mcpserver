"""MaxKB MCP Server - Knowledge Base Retrieval via MCP Protocol."""

import json

from fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware

from .client import MaxKBClient
from .config import settings
from .models import ChatRequest, SearchRequest

# Initialize MaxKB client
maxkb_client: MaxKBClient | None = None


async def get_client() -> MaxKBClient:
    """Get or create MaxKB client."""
    global maxkb_client
    if maxkb_client is None:
        maxkb_client = MaxKBClient()
    return maxkb_client


# Initialize MCP Server
mcp = FastMCP(settings.mcp_server_name)


@mcp.tool()
async def list_knowledge_bases() -> str:
    """列出所有可用的知识库。

    Returns:
        包含知识库列表的 JSON 字符串，包含 id、名称、描述等信息
    """
    client = await get_client()
    kb_list = await client.list_knowledge_bases()

    result = []
    for kb in kb_list:
        result.append({
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "document_count": kb.document_count,
        })

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_knowledge_base_info(knowledge_base_id: str) -> str:
    """获取指定知识库的详细信息。

    Args:
        knowledge_base_id: 要查询的知识库 ID

    Returns:
        包含知识库详细信息的 JSON 字符串
    """
    client = await get_client()
    kb = await client.get_knowledge_base(knowledge_base_id)

    if kb is None:
        return json.dumps(
            {"error": "未找到知识库"},
            ensure_ascii=False,
        )

    result = {
        "id": kb.id,
        "name": kb.name,
        "description": kb.description,
        "document_count": kb.document_count,
        "create_time": kb.create_time,
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def search_knowledge_base(
    query: str,
    knowledge_base_id: str,
    top_k: int = 5,
) -> str:
    """在知识库中搜索相关内容。

    Args:
        query: 搜索查询文本
        knowledge_base_id: 要搜索的知识库 ID
        top_k: 返回结果数量（1-20，默认 5）

    Returns:
        包含搜索结果和相似度评分的 JSON 字符串
    """
    client = await get_client()

    request = SearchRequest(
        query=query,
        knowledge_base_id=knowledge_base_id,
        top_k=top_k,
    )

    response = await client.search(request)

    result = {
        "query": query,
        "total": response.total,
        "results": [
            {
                "content": r.content,
                "title": r.title,
                "source": r.source,
                "similarity": r.similarity,
            }
            for r in response.results
        ],
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def ask_question(
    question: str,
    knowledge_base_id: str,
) -> str:
    """向知识库提问并获取 AI 生成的答案。

    Args:
        question: 要问的问题
        knowledge_base_id: 要查询的知识库 ID

    Returns:
        包含答案和引用文档的 JSON 字符串
    """
    client = await get_client()

    request = ChatRequest(
        message=question,
        knowledge_base_id=knowledge_base_id,
    )

    response = await client.chat(request)

    result = {
        "question": question,
        "answer": response.answer,
        "references": [
            {
                "content": r.content,
                "title": r.title,
                "source": r.source,
                "similarity": r.similarity,
            }
            for r in response.references
        ],
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.resource("knowledge-bases://list")
async def list_knowledge_bases_resource() -> str:
    """资源：列出所有知识库。

    Returns:
        知识库列表的 JSON 字符串
    """
    return await list_knowledge_bases()


@mcp.resource("knowledge-base://{knowledge_base_id}")
async def get_knowledge_base_resource(knowledge_base_id: str) -> str:
    """资源：获取知识库详情。

    Args:
        knowledge_base_id: 知识库 ID

    Returns:
        知识库详情的 JSON 字符串
    """
    return await get_knowledge_base_info(knowledge_base_id)


@mcp.prompt()
def knowledge_base_search_prompt(query: str, knowledge_base_name: str) -> str:
    """知识库搜索的提示词模板。

    Args:
        query: 用户的搜索查询
        knowledge_base_name: 知识库名称

    Returns:
        格式化后的提示词字符串
    """
    return f"""你是一个有帮助的助手，可以访问"{knowledge_base_name}"知识库。

用户正在询问：{query}

请在知识库中搜索相关信息，并根据搜索结果提供全面的回答。如果搜索结果中没有足够的信息，请告知用户。

回答时请注意：
1. 使用知识库中的信息
2. 尽可能引用具体来源
3. 简洁但全面
4. 如果信息不完整，请说明局限性
"""


def create_starlette_app(mcp_server: FastMCP) -> Starlette:
    """Create Starlette application with SSE support."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server._mcp_server.run(
                streams[0], streams[1], mcp_server._mcp_server.create_initialization_options()
            )

    async def handle_messages(request):
        """Handle POST messages from client."""
        return await sse.handle_post_message(request.scope, request.receive, request._send)

    app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages/", endpoint=handle_messages, methods=["POST"]),
        ],
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def main() -> None:
    """Run the MCP server."""
    transport = settings.mcp_transport

    if transport == "sse":
        import uvicorn
        print(f"Starting MCP server with SSE transport on http://{settings.mcp_host}:{settings.mcp_port}")
        print(f"SSE endpoint: http://{settings.mcp_host}:{settings.mcp_port}/sse")
        app = create_starlette_app(mcp)
        uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)
    else:
        print(f"Starting MCP server with stdio transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
