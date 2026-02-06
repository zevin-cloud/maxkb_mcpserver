"""Test get knowledge base info."""
import asyncio
from src.client import MaxKBClient

async def test():
    print("Testing get knowledge base info...")
    print("="*60)
    
    client = MaxKBClient()
    
    try:
        kb_id = "01990834-d745-76c1-9827-da5dc8e49d18"
        print(f"\nKnowledge Base ID: {kb_id}")
        
        kb = await client.get_knowledge_base(kb_id)
        
        if kb:
            print(f"Name: {kb.name}")
            print(f"Description: {kb.description}")
            print(f"Document Count: {kb.document_count}")
            print(f"Create Time: {kb.create_time}")
        else:
            print("Knowledge base not found or no data returned")
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test())
