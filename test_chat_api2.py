"""Test MaxKB chat API with correct endpoint."""
import asyncio
import httpx

API_KEY = "user-e231ba6ec07aa0a491117a2a7abae662"
BASE_URL = "https://mk2.lovekd.top:20000"
WORKSPACE = "default"

async def test_chat_api():
    """Test the correct chat API endpoint."""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        # Get knowledge bases (applications)
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
                
                # Test OpenAI compatible chat endpoint
                path = f"/chat/api/{kb_id}/chat/completions"
                url = f"{BASE_URL}{path}"
                
                # OpenAI compatible payload
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": "你好，请介绍一下自己"}
                    ],
                    "stream": False
                }
                
                print(f"\n{'='*60}")
                print(f"Testing: POST {path}")
                print(f"Payload: {payload}")
                print('='*60)
                
                try:
                    response = await client.post(url, headers=headers, json=payload)
                    print(f"\nStatus: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"SUCCESS!")
                        print(f"Response: {response.text[:1000]}")
                    elif response.status_code in (301, 302, 307, 308):
                        print(f"Redirect to: {response.headers.get('location', 'N/A')}")
                    else:
                        print(f"Response: {response.text[:500]}")
                        
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_api())
