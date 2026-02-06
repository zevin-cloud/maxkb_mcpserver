"""Test MCP API with updated client."""
import asyncio
from src.client import MaxKBClient

async def test():
    print("Testing MaxKB MCP API...")
    print("="*60)
    
    client = MaxKBClient()
    
    try:
        # Test 1: List knowledge bases
        print("\n1. Testing list_knowledge_bases...")
        kb_list = await client.list_knowledge_bases()
        print(f"   Found {len(kb_list)} knowledge bases:")
        for kb in kb_list:
            print(f"   - {kb.name} (ID: {kb.id})")
        
        if kb_list:
            kb_id = kb_list[0].id
            
            # Test 2: Get knowledge base info
            print(f"\n2. Testing get_knowledge_base_info ({kb_id})...")
            kb_info = await client.get_knowledge_base(kb_id)
            if kb_info:
                print(f"   Name: {kb_info.name}")
                print(f"   Description: {kb_info.description}")
            else:
                print("   Not found")
            
            # Test 3: Search knowledge base
            print(f"\n3. Testing search_knowledge_base...")
            from src.models import SearchRequest
            search_req = SearchRequest(
                query="测试",
                knowledge_base_id=kb_id,
                top_k=3
            )
            search_result = await client.search(search_req)
            print(f"   Found {search_result.total} results")
            for i, r in enumerate(search_result.results[:3], 1):
                print(f"   {i}. {r.title} (相似度: {r.similarity:.2f})")
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test())
