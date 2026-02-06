"""Test search with different queries and parameters."""
import asyncio
from src.client import MaxKBClient
from src.models import SearchRequest

async def test():
    print("Testing search with different parameters...")
    print("="*60)
    
    client = MaxKBClient()
    
    # 测试不同的查询词和参数
    test_cases = [
        {
            "query": "飞书端操作",
            "similarity": 0.5,
            "search_mode": "embedding"
        },
        {
            "query": "北港物流",
            "similarity": 0.5,
            "search_mode": "embedding"
        },
        {
            "query": "操作手册",
            "similarity": 0.4,
            "search_mode": "embedding"
        },
        {
            "query": "镔鑫钢铁",
            "similarity": 0.5,
            "search_mode": "keywords"
        },
    ]
    
    try:
        for i, tc in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {tc['query']}")
            print(f"  Similarity: {tc['similarity']}, Mode: {tc['search_mode']}")
            
            request = SearchRequest(
                query=tc['query'],
                knowledge_base_id="01990834-d745-76c1-9827-da5dc8e49d18",
                top_k=5,
                similarity=tc['similarity'],
                search_mode=tc['search_mode']
            )
            
            response = await client.search(request)
            print(f"  Results: {response.total} found")
            
            for j, r in enumerate(response.results[:3], 1):
                print(f"    {j}. [{r.similarity:.2%}] {r.title or 'No title'}")
                
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test())
