"""Test search with specific knowledge base."""
import asyncio
from src.client import MaxKBClient
from src.models import SearchRequest

async def test():
    print("Testing search...")
    print("="*60)
    
    client = MaxKBClient()
    
    try:
        request = SearchRequest(
            query="镔鑫钢铁集团北港物流飞书端操作手册",
            knowledge_base_id="01990834-d745-76c1-9827-da5dc8e49d18",
            top_k=5,
            similarity=0.6,
            search_mode="embedding"
        )
        
        print(f"\nSearch request:")
        print(f"  Query: {request.query}")
        print(f"  Knowledge Base ID: {request.knowledge_base_id}")
        print(f"  Top K: {request.top_k}")
        print(f"  Similarity: {request.similarity}")
        print(f"  Search Mode: {request.search_mode}")
        
        response = await client.search(request)
        
        print(f"\nResults: {response.total} found")
        for i, r in enumerate(response.results, 1):
            print(f"\n{i}. [{r.similarity:.2%}] {r.title}")
            print(f"   Source: {r.source}")
            print(f"   Content: {r.content[:200]}...")
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test())
