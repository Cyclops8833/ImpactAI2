import requests
import sys
from urllib.parse import urljoin

def test_deployment(backend_url, frontend_url=None):
    """Test if deployment is working correctly"""
    
    print("🔍 Testing ImpactAI Deployment...")
    print(f"Backend URL: {backend_url}")
    if frontend_url:
        print(f"Frontend URL: {frontend_url}")
    
    # Test backend health
    try:
        health_response = requests.get(urljoin(backend_url, "/api/health"), timeout=10)
        if health_response.status_code == 200:
            print("✅ Backend health check passed!")
            health_data = health_response.json()
            print(f"   Database status: {health_data.get('database', 'unknown')}")
        else:
            print(f"❌ Backend health check failed! Status: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {str(e)}")
        return False
    
    # Test quote creation endpoint
    try:
        test_quote = {
            "client_name": "Deployment Test",
            "product_type": "Flyer",
            "finished_size": "A4 (210 × 297mm)",
            "page_count": 1,
            "sidedness": "single",
            "quantity": 100,
            "delivery_location": "Metro Melbourne",
            "ink_type": "CMYK",
            "pms_colors": False,
            "pms_color_count": 1,
            "finishing_options": []
        }
        
        quote_response = requests.post(
            urljoin(backend_url, "/api/quotes"), 
            json=test_quote, 
            timeout=10
        )
        
        if quote_response.status_code == 200:
            print("✅ Quote creation test passed!")
            quote_data = quote_response.json()
            print(f"   Test quote ID: {quote_data.get('quote_id')}")
            print(f"   Estimated cost: ${quote_data.get('estimated_cost', 0):.2f}")
        else:
            print(f"❌ Quote creation test failed! Status: {quote_response.status_code}")
            print(f"   Response: {quote_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Quote creation test failed: {str(e)}")
        return False
    
    # Test frontend (if URL provided)
    if frontend_url:
        try:
            frontend_response = requests.get(frontend_url, timeout=10)
            if frontend_response.status_code == 200:
                print("✅ Frontend is accessible!")
            else:
                print(f"⚠️  Frontend returned status: {frontend_response.status_code}")
        except Exception as e:
            print(f"⚠️  Frontend test failed: {str(e)}")
    
    print("\n🎉 Deployment test completed successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_deployment.py <backend_url> [frontend_url]")
        print("Example: python test_deployment.py https://impactai-backend.onrender.com")
        sys.exit(1)
    
    backend_url = sys.argv[1]
    frontend_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_deployment(backend_url, frontend_url)
    sys.exit(0 if success else 1)