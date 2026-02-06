"""Test MaxKB API connection."""
import asyncio
import httpx

API_KEY = "user-e231ba6ec07aa0a491117a2a7ae662"
BASE_URL = "https://mk2.lovekd.top:20000"

async def test_auth_methods():
    """Test different authentication methods."""
    
    auth_methods = [
        ("Bearer Token", {"Authorization": f"Bearer {API_KEY}"}),
        ("X-API-KEY Header", {"X-API-KEY": API_KEY}),
        ("API-Key Header", {"API-Key": API_KEY}),
        ("X-Token Header", {"X-Token": API_KEY}),
    ]
    
    paths = [
        "/api/dataset",
        "/api/v1/dataset", 
        "/api/application",
        "/api/v1/application",
    ]
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        for auth_name, headers in auth_methods:
            print(f"\n{'='*60}")
            print(f"Testing: {auth_name}")
            print(f"Headers: {headers}")
            print('='*60)
            
            for path in paths:
                url = f"{BASE_URL}{path}"
                try:
                    response = await client.get(url, headers=headers)
                    print(f"\n  {path}")
                    print(f"    Status: {response.status_code}")
                    print(f"    Content-Type: {response.headers.get('content-type', 'N/A')}")
                    
                    if response.status_code == 200:
                        content_preview = response.text[:200]
                        print(f"    Preview: {content_preview}...")
                    elif response.status_code in (301, 302, 307, 308):
                        location = response.headers.get('location', 'N/A')
                        print(f"    Redirect to: {location}")
                    else:
                        print(f"    Response: {response.text[:200]}")
                        
                except Exception as e:
                    print(f"\n  {path}")
                    print(f"    Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_methods())
