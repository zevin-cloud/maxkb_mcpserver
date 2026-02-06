"""Test MaxKB API connection with provided key."""
import asyncio
import httpx

API_KEY = "user-e231ba6ec07aa0a491117a2a7abae662"
BASE_URL = "https://mk2.lovekd.top:20000"

async def test_more_auth_methods():
    """Test more authentication methods and paths."""
    
    # More auth methods
    auth_methods = [
        ("Bearer Token", {"Authorization": f"Bearer {API_KEY}"}),
        ("Token Header", {"Token": API_KEY}),
        ("X-Auth-Token", {"X-Auth-Token": API_KEY}),
        ("X-Access-Token", {"X-Access-Token": API_KEY}),
        ("Cookie Style", {"Cookie": f"token={API_KEY}"}),
    ]
    
    # More paths to test
    paths = [
        "/api/dataset",
        "/api/v1/dataset",
        "/api/application",
        "/api/v1/application",
        "/api/chat",
        "/api/v1/chat",
        "/api/user",
        "/api/v1/user",
    ]
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        for auth_name, headers in auth_methods:
            print(f"\n{'='*60}")
            print(f"Testing: {auth_name}")
            print('='*60)
            
            for path in paths:
                url = f"{BASE_URL}{path}"
                try:
                    response = await client.get(url, headers=headers)
                    if response.status_code != 302:  # Only show non-redirect responses
                        print(f"\n  {path}")
                        print(f"    Status: {response.status_code}")
                        print(f"    Content-Type: {response.headers.get('content-type', 'N/A')}")
                        if response.status_code == 200:
                            print(f"    SUCCESS! Preview: {response.text[:100]}...")
                        
                except Exception as e:
                    pass  # Ignore errors

if __name__ == "__main__":
    asyncio.run(test_more_auth_methods())
