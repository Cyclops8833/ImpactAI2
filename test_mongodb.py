#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test for ImpactAI Quote Assistant
Run this script to verify your MongoDB Atlas setup before deployment
"""

import sys
import os
from pymongo import MongoClient
from datetime import datetime

def test_mongodb_connection(connection_string):
    """Test MongoDB Atlas connection with detailed feedback"""
    
    print("🔍 Testing MongoDB Atlas Connection...")
    print(f"Connection String: {connection_string[:50]}...{connection_string[-20:]}")
    print("-" * 60)
    
    try:
        # Create client
        print("1️⃣ Creating MongoDB client...")
        client = MongoClient(connection_string)
        
        # Test connection
        print("2️⃣ Testing connection...")
        client.admin.command('ping')
        print("   ✅ Connection successful!")
        
        # Test database access
        print("3️⃣ Testing database access...")
        db = client.impactai_quotes
        collection = db.quotes
        
        # Insert test document
        print("4️⃣ Testing write permissions...")
        test_doc = {
            "test": True,
            "message": "MongoDB Atlas connection test",
            "timestamp": datetime.utcnow(),
            "app": "ImpactAI Quote Assistant"
        }
        
        result = collection.insert_one(test_doc)
        print(f"   ✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read test document
        print("5️⃣ Testing read permissions...")
        found_doc = collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("   ✅ Test document retrieved successfully!")
        
        # Clean up test document
        print("6️⃣ Cleaning up test data...")
        collection.delete_one({"_id": result.inserted_id})
        print("   ✅ Test document cleaned up!")
        
        # Get database stats
        print("7️⃣ Getting database information...")
        stats = db.command("dbstats")
        print(f"   📊 Database size: {stats.get('dataSize', 0)} bytes")
        print(f"   📊 Collections: {stats.get('collections', 0)}")
        
        print("\n🎉 MongoDB Atlas setup is PERFECT!")
        print("🚀 Ready for deployment!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check username and password in connection string")
        print("2. Verify IP address is whitelisted (0.0.0.0/0 for production)")
        print("3. Ensure database user has 'Read and write' permissions")
        print("4. Check if cluster is still spinning up (wait 2-3 minutes)")
        return False
    
    finally:
        try:
            client.close()
        except:
            pass

def main():
    """Main function to test MongoDB connection"""
    print("🗄️  MongoDB Atlas Connection Tester")
    print("=" * 60)
    
    # Get connection string
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        connection_string = input("📝 Enter your MongoDB Atlas connection string: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided!")
        return False
    
    # Validate connection string format
    if not connection_string.startswith('mongodb+srv://'):
        print("❌ Invalid connection string format!")
        print("💡 Should start with: mongodb+srv://")
        return False
    
    if '<password>' in connection_string:
        print("❌ Don't forget to replace <password> with your actual password!")
        return False
    
    # Test connection
    success = test_mongodb_connection(connection_string)
    
    if success:
        print("\n📋 Next Steps:")
        print("1. Save this connection string as MONGO_URL environment variable")
        print("2. Push your code to GitHub")
        print("3. Deploy to Render/Vercel")
        print("4. Add MONGO_URL to your deployment environment variables")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)