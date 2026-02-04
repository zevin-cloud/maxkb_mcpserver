"""Pydantic models for MaxKB API and MCP Server."""

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeBase(BaseModel):
    """Knowledge base information."""

    id: str = Field(description="Knowledge base ID")
    name: str = Field(description="Knowledge base name")
    description: str = Field(default="", description="Knowledge base description")
    document_count: int = Field(default=0, description="Number of documents in the KB")
    create_time: str = Field(default="", description="Creation time")


class SearchResult(BaseModel):
    """Search result from knowledge base."""

    content: str = Field(description="Retrieved content")
    title: str = Field(default="", description="Document title")
    source: str = Field(default="", description="Source document")
    similarity: float = Field(default=0.0, description="Similarity score")


class SearchRequest(BaseModel):
    """Search request parameters."""

    query: str = Field(description="Search query")
    knowledge_base_id: str = Field(description="Target knowledge base ID")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class SearchResponse(BaseModel):
    """Search response."""

    results: list[SearchResult] = Field(default_factory=list, description="Search results")
    total: int = Field(default=0, description="Total results found")


class ChatMessage(BaseModel):
    """Chat message."""

    role: str = Field(description="Message role: user/assistant")
    content: str = Field(description="Message content")


class ChatRequest(BaseModel):
    """Chat request parameters."""

    message: str = Field(description="User message")
    knowledge_base_id: str = Field(description="Target knowledge base ID")
    history: list[ChatMessage] = Field(
        default_factory=list, description="Chat history"
    )


class ChatResponse(BaseModel):
    """Chat response."""

    answer: str = Field(description="AI answer")
    references: list[SearchResult] = Field(
        default_factory=list, description="Referenced documents"
    )


class MaxKBResponse(BaseModel):
    """Generic MaxKB API response wrapper."""

    code: int = Field(description="Response code")
    message: str = Field(description="Response message")
    data: Any = Field(default=None, description="Response data")
