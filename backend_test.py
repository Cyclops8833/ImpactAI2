#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from pprint import pprint

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

# Ensure we have a valid backend URL
if not BACKEND_URL:
    print("Error: Could not find REACT_APP_BACKEND_URL in frontend/.env")
    sys.exit(1)

# Add /api prefix for all API endpoints
API_URL = f"{BACKEND_URL}/api"

print(f"Using API URL: {API_URL}")

# Test data as specified in the review request
test_quote_data = {
    "client_name": "Test Print Co",
    "product_type": "Brochure",
    "finished_size": "A4 (210 × 297mm)",
    "page_count": 8,
    "sidedness": "double",
    "cover_stock": "300gsm Gloss Art",
    "text_stock": "150gsm Gloss Art",
    "finishing_options": ["Matt Laminate", "Foiling (Other)"],
    "quantity": 1000,
    "delivery_location": "Metro Melbourne",
    "special_requirements": "Test quote for API validation",
    "ink_type": "CMYK",
    "pms_colors": True,
    "pms_color_count": 2
}

# Store created quote IDs for later tests
created_quotes = []

def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check API ===")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Health check successful!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Health check failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during health check: {str(e)}")
        return False

def test_create_quote():
    """Test quote creation API"""
    print("\n=== Testing Quote Creation API ===")
    try:
        response = requests.post(f"{API_URL}/quotes", json=test_quote_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            quote_data = response.json()
            print("Quote created successfully!")
            print("Quote details:")
            pprint(quote_data)
            
            # Save quote ID for later tests
            created_quotes.append(quote_data["quote_id"])
            
            # Verify all required fields are present
            required_fields = ["quote_id", "client_name", "product_type", "estimated_cost", "created_at", "status"]
            missing_fields = [field for field in required_fields if field not in quote_data]
            
            if missing_fields:
                print(f"Warning: Missing fields in response: {missing_fields}")
                return False
            
            print("All required fields present in response.")
            return True
        else:
            print(f"Quote creation failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during quote creation: {str(e)}")
        return False

def test_create_quote_validation():
    """Test quote creation validation"""
    print("\n=== Testing Quote Creation Validation ===")
    
    # Test with missing required fields
    invalid_data = test_quote_data.copy()
    del invalid_data["client_name"]  # Remove a required field
    
    try:
        response = requests.post(f"{API_URL}/quotes", json=invalid_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print("Validation correctly rejected missing required field.")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Unexpected status code {response.status_code} for validation test")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during validation test: {str(e)}")
        return False

def test_get_quotes():
    """Test quote listing API"""
    print("\n=== Testing Quote Listing API ===")
    try:
        response = requests.get(f"{API_URL}/quotes")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            quotes = response.json()
            print(f"Retrieved {len(quotes)} quotes")
            
            if quotes:
                print("Sample quote:")
                pprint(quotes[0])
            
            return True
        else:
            print(f"Quote listing failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during quote listing: {str(e)}")
        return False

def test_get_quote_detail():
    """Test quote detail API"""
    print("\n=== Testing Quote Detail API ===")
    
    if not created_quotes:
        print("No quotes created yet, skipping test")
        return False
    
    quote_id = created_quotes[0]
    try:
        response = requests.get(f"{API_URL}/quotes/{quote_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            quote = response.json()
            print("Quote details retrieved successfully!")
            
            # Verify all fields are present including new ones
            required_fields = [
                "quote_id", "client_name", "product_type", "estimated_cost", 
                "created_at", "status", "finished_size", "page_count", 
                "sidedness", "cover_stock", "text_stock", "finishing_options", 
                "quantity", "delivery_location", "special_requirements",
                "ink_type", "pms_colors", "pms_color_count"
            ]
            
            missing_fields = [field for field in required_fields if field not in quote]
            
            if missing_fields:
                print(f"Warning: Missing fields in response: {missing_fields}")
                return False
            
            print("All required fields present in quote detail.")
            
            # Verify new fields have correct values
            if quote["ink_type"] != test_quote_data["ink_type"]:
                print(f"Warning: ink_type mismatch. Expected: {test_quote_data['ink_type']}, Got: {quote['ink_type']}")
            
            if quote["pms_colors"] != test_quote_data["pms_colors"]:
                print(f"Warning: pms_colors mismatch. Expected: {test_quote_data['pms_colors']}, Got: {quote['pms_colors']}")
            
            if quote["pms_color_count"] != test_quote_data["pms_color_count"]:
                print(f"Warning: pms_color_count mismatch. Expected: {test_quote_data['pms_color_count']}, Got: {quote['pms_color_count']}")
            
            return True
        else:
            print(f"Quote detail retrieval failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during quote detail retrieval: {str(e)}")
        return False

def test_update_quote_status():
    """Test quote status update API"""
    print("\n=== Testing Quote Status Update API ===")
    
    if not created_quotes:
        print("No quotes created yet, skipping test")
        return False
    
    quote_id = created_quotes[0]
    new_status = "approved"
    
    try:
        response = requests.put(f"{API_URL}/quotes/{quote_id}/status?status={new_status}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Quote status updated to '{new_status}' successfully!")
            print(f"Response: {response.json()}")
            
            # Verify the status was actually updated
            detail_response = requests.get(f"{API_URL}/quotes/{quote_id}")
            if detail_response.status_code == 200:
                quote = detail_response.json()
                if quote["status"] == new_status:
                    print("Status update confirmed in quote details.")
                    return True
                else:
                    print(f"Status update failed. Expected: {new_status}, Got: {quote['status']}")
                    return False
            else:
                print("Could not verify status update.")
                return False
        else:
            print(f"Quote status update failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during quote status update: {str(e)}")
        return False

def test_export_quote():
    """Test quote export API"""
    print("\n=== Testing Quote Export API ===")
    
    if not created_quotes:
        print("No quotes created yet, skipping test")
        return False
    
    quote_id = created_quotes[0]
    try:
        response = requests.get(f"{API_URL}/quotes/{quote_id}/export")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            content_disposition = response.headers.get('Content-Disposition')
            
            print(f"Content-Type: {content_type}")
            print(f"Content-Disposition: {content_disposition}")
            
            if content_type == "application/pdf":
                print("PDF export successful!")
                
                # Save the PDF to verify it's valid
                pdf_path = f"/tmp/quote_{quote_id}.pdf"
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"PDF saved to {pdf_path}")
                
                # Check file size to ensure it's not empty
                file_size = os.path.getsize(pdf_path)
                print(f"PDF file size: {file_size} bytes")
                
                if file_size > 0:
                    print("PDF file is not empty, export successful.")
                    return True
                else:
                    print("Warning: PDF file is empty.")
                    return False
            else:
                print(f"Unexpected content type: {content_type}")
                return False
        else:
            print(f"Quote export failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during quote export: {str(e)}")
        return False

def test_invalid_quote_id():
    """Test error handling with invalid quote ID"""
    print("\n=== Testing Invalid Quote ID Handling ===")
    
    invalid_id = "INVALID1"
    try:
        response = requests.get(f"{API_URL}/quotes/{invalid_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("Correctly returned 404 for invalid quote ID.")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Unexpected status code {response.status_code} for invalid ID test")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during invalid ID test: {str(e)}")
        return False

def test_delete_quote():
    """Test quote deletion API"""
    print("\n=== Testing Quote Deletion API ===")
    
    if not created_quotes:
        print("No quotes created yet, skipping test")
        return False
    
    quote_id = created_quotes[0]
    try:
        response = requests.delete(f"{API_URL}/quotes/{quote_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Quote deleted successfully!")
            print(f"Response: {response.json()}")
            
            # Verify the quote was actually deleted
            detail_response = requests.get(f"{API_URL}/quotes/{quote_id}")
            if detail_response.status_code == 404:
                print("Deletion confirmed - quote no longer exists.")
                created_quotes.remove(quote_id)
                return True
            else:
                print(f"Deletion verification failed. Expected 404, Got: {detail_response.status_code}")
                return False
        else:
            print(f"Quote deletion failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during quote deletion: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n======= PRINT QUOTE ASSISTANT API TESTS =======")
    print(f"Testing against API URL: {API_URL}")
    print("===============================================\n")
    
    test_results = {
        "Health Check": test_health_check(),
        "Quote Creation": test_create_quote(),
        "Form Validation": test_create_quote_validation(),
        "Quote Listing": test_get_quotes(),
        "Quote Detail": test_get_quote_detail(),
        "Status Update": test_update_quote_status(),
        "Quote Export": test_export_quote(),
        "Invalid Quote ID": test_invalid_quote_id(),
        "Quote Deletion": test_delete_quote()
    }
    
    print("\n======= TEST RESULTS SUMMARY =======")
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        if not result:
            all_passed = False
        print(f"{test_name}: {status}")
    
    print("\n======= OVERALL RESULT =======")
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()