"""Test MaxKB API with correct paths."""
import asyncio
import httpx

API_KEY = "user-e231ba6ec07aa0a491117a2a7abae662"
BASE_URL = "https://mk2.lovekd.top:20000"

async def test_correct_api():
    """Test with correct API paths and auth."""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Test paths - need workspace_id
    paths = [
        "/admin/api/workspace",  # List workspaces
        "/admin/api/workspace/default/knowledge",  # Default workspace knowledge
    ]
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        for path in paths:
            url = f"{BASE_URL}{path}"
            try:
                response = await client.get(url, headers=headers)
                print(f"\n{'='*60}")
                print(f"Path: {path}")
                print(f"Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status_code == 200:
                    print(f"SUCCESS!")
                    print(f"Response: {response.text[:500]}")
                elif response.status_code in (301, 302, 307, 308):
                    print(f"Redirect to: {response.headers.get('location', 'N/A')}")
                elif response.status_code == 404:
                    print(f"Not found")
                else:
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"\n{path}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_correct_api())
