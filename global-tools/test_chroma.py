#!/usr/bin/env python3
"""
Simple script to test ChromaDB connection with authentication
"""

import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

def main():
    """Test ChromaDB connection"""
    print("🔍 Testing ChromaDB Connection...")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ["CHROMA_HOST", "CHROMA_PORT", "CHROMA_SERVER_AUTHN_CREDENTIALS"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set them in your .env file:")
        print("CHROMA_HOST=your-chroma-host")
        print("CHROMA_PORT=8000")
        print("CHROMA_SERVER_AUTHN_CREDENTIALS=your-auth-token")
        return False
    
    print("✅ Environment variables found:")
    print(f"  CHROMA_HOST: {os.getenv('CHROMA_HOST')}")
    print(f"  CHROMA_PORT: {os.getenv('CHROMA_PORT')}")
    print(f"  CHROMA_SERVER_AUTHN_CREDENTIALS: {'***' + os.getenv('CHROMA_SERVER_AUTHN_CREDENTIALS', '')[-4:]}")
    print()
    
    try:
        # Import the test function
        from chromaManager import test_chroma_connection
        
        print("🔌 Testing connection...")
        client = test_chroma_connection()
        
        if client:
            print("✅ Successfully connected to ChromaDB!")
            
            # Test basic operations
            print("\n🧪 Testing basic operations...")
            
            # List collections
            try:
                collections = client.list_collections()
                print(f"✅ Listed collections: {len(collections)} found")
                for col in collections:
                    print(f"  - {col.name}")
            except Exception as e:
                print(f"⚠️  Error listing collections: {str(e)}")
            
            # Test creating a collection
            try:
                test_collection = client.get_or_create_collection("test_connection")
                print("✅ Successfully created/accessed test collection")
                
                # Clean up
                try:
                    client.delete_collection("test_connection")
                    print("✅ Cleaned up test collection")
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️  Error with test collection: {str(e)}")
            
            print("\n🎉 ChromaDB connection test completed successfully!")
            return True
            
    except SystemExit:
        print("❌ ChromaDB connection test failed (system exit)")
        return False
    except Exception as e:
        print(f"❌ ChromaDB connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("1. Check that ChromaDB server is running")
        print("2. Verify your authentication credentials")
        print("3. Ensure network connectivity to the ChromaDB host")
        print("4. Check ChromaDB server logs for authentication errors")
        exit(1)
    else:
        print("\n✅ Ready to run the full API!")
        exit(0) 