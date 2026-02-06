"""Test MaxKB chat API."""
import asyncio
import httpx

API_KEY = "user-e231ba6ec07aa0a491117a2a7abae662"
BASE_URL = "https://mk2.lovekd.top:20000"
WORKSPACE = "default"

async def test_chat_api():
    """Test different chat API endpoints."""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    # 先获取知识库列表
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        # Get knowledge bases
        resp = await client.get(
            f"{BASE_URL}/admin/api/workspace/{WORKSPACE}/knowledge",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("data"):
                kb_id = data["data"][0]["id"]
                kb_name = data["data"][0]["name"]
                print(f"Using knowledge base: {kb_name} (ID: {kb_id})")
                
                # Test different chat endpoints
                chat_endpoints = [
                    # (method, path, payload)
                    ("POST", f"/admin/api/workspace/{WORKSPACE}/application/{kb_id}/chat", {"message": "你好", "re_chat": False, "stream": False}),
                    ("POST", f"/admin/api/chat/open/{kb_id}", {"message": "你好"}),
                    ("POST", f"/admin/api/chat/{kb_id}", {"message": "你好"}),
                ]
                
                for method, path, payload in chat_endpoints:
                    url = f"{BASE_URL}{path}"
                    try:
                        response = await client.request(method, url, headers=headers, json=payload)
                        print(f"\n{'='*60}")
                        print(f"Endpoint: {method} {path}")
                        print(f"Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            print(f"SUCCESS!")
                            print(f"Response: {response.text[:500]}")
                            break  # Found working endpoint
                        elif response.status_code in (301, 302, 307, 308):
                            print(f"Redirect to: {response.headers.get('location', 'N/A')}")
                        else:
                            print(f"Response: {response.text[:200]}")
                            
                    except Exception as e:
                        print(f"\n{path}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_api())
