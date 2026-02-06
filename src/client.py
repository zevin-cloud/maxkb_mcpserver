"""MaxKB API client."""

import httpx

from .config import settings
from .models import (
    KnowledgeBase,
    MaxKBResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)


class MaxKBClient:
    """Client for MaxKB API."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None, workspace_id: str | None = None):
        """Initialize MaxKB client.

        Args:
            base_url: MaxKB API base URL
            api_key: API key for authentication
            workspace_id: MaxKB workspace ID
        """
        self.base_url = (base_url or settings.maxkb_api_base).rstrip("/")
        self.api_key = api_key or settings.maxkb_api_key
        self.workspace_id = workspace_id or settings.maxkb_workspace_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            follow_redirects=False,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> MaxKBResponse:
        """Make HTTP request to MaxKB API.

        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional request parameters

        Returns:
            Parsed API response
        """
        url = f"{self.base_url}{path}"
        response = await self.client.request(method, url, **kwargs)
        
        # Handle redirect (authentication error)
        if response.status_code in (301, 302, 307, 308):
            location = response.headers.get('location', '')
            if '/admin' in location or '/login' in location:
                raise Exception(
                    f"MaxKB API 认证失败，API Key 可能已过期或无效。"
                    f"请检查 .env 文件中的 MAXKB_API_KEY 配置。"
                )
            else:
                raise Exception(
                    f"MaxKB API 返回重定向 (HTTP {response.status_code}) 到: {location}"
                )
        
        response.raise_for_status()
        data = response.json()
        return MaxKBResponse(**data)

    async def list_knowledge_bases(self) -> list[KnowledgeBase]:
        """List all knowledge bases.

        Returns:
            List of knowledge bases
        """
        resp = await self._request("GET", f"/workspace/{self.workspace_id}/knowledge")
        if resp.code != 200 or not resp.data:
            return []

        kb_list = []
        for item in resp.data:
            kb = KnowledgeBase(
                id=str(item.get("id", "")),
                name=item.get("name", ""),
                description=item.get("desc", ""),
                document_count=item.get("document_count") or 0,
                create_time=item.get("create_time", ""),
            )
            kb_list.append(kb)
        return kb_list

    async def get_knowledge_base(self, kb_id: str) -> KnowledgeBase | None:
        """Get knowledge base details.

        Args:
            kb_id: Knowledge base ID

        Returns:
            Knowledge base info or None if not found
        """
        resp = await self._request("GET", f"/workspace/{self.workspace_id}/knowledge/{kb_id}")
        if resp.code != 200 or not resp.data:
            return None

        data = resp.data
        return KnowledgeBase(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            description=data.get("desc", ""),
            document_count=data.get("document_count") or 0,
            create_time=data.get("create_time", ""),
        )

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Search knowledge base.

        Args:
            request: Search request parameters

        Returns:
            Search results
        """
        payload = {
            "query_text": request.query,
            "top_number": request.top_k,
            "search_mode": request.search_mode,
            "similarity": request.similarity,
        }

        resp = await self._request(
            "POST",
            f"/workspace/{self.workspace_id}/knowledge/{request.knowledge_base_id}/hit_test",
            json=payload,
        )

        if resp.code != 200 or not resp.data:
            return SearchResponse(results=[], total=0)

        results = []
        for item in resp.data:
            result = SearchResult(
                content=item.get("content", ""),
                title=item.get("title", ""),
                source=item.get("source", ""),
                similarity=item.get("similarity", 0.0),
            )
            results.append(result)

        return SearchResponse(results=results, total=len(results))
