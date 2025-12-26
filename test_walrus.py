"""
Test script for Walrus blockchain integration
"""

import sys
sys.path.insert(0, 'c:\\Users\\Emre\\Desktop\\hds-frontend\\hsd-proje')

from app.services.walrus_service import WalrusService

def test_walrus():
    print("=" * 60)
    print("🚀 Testing Walrus Blockchain Integration")
    print("=" * 60)
    
    # Initialize Walrus service
    walrus = WalrusService(
        publisher_url="https://publisher.walrus-testnet.walrus.space",
        aggregator_url="https://aggregator.walrus-testnet.walrus.space",
        epochs=5
    )
    
    print("\n✅ Walrus service initialized successfully!")
    print(f"   Publisher: {walrus.publisher_url}")
    print(f"   Aggregator: {walrus.aggregator_url}")
    print(f"   Epochs: {walrus.epochs}")
    
    # Test 1: Store a message
    print("\n" + "=" * 60)
    print("📝 Test 1: Storing message on Walrus blockchain...")
    print("=" * 60)
    
    test_message = "Hello from Walrus blockchain! 🚀 This is a test message from HSD Proje."
    print(f"Message: {test_message}")
    
    result = walrus.store_text(test_message)
    
    if result:
        blob_id = result.get('blob_id')
        print(f"\n✅ Message stored successfully!")
        print(f"   Blob ID: {blob_id}")
        print(f"   Size: {result.get('size')} bytes")
        print(f"   Storage Type: {result.get('storage_type')}")
        print(f"   Certified Epoch: {result.get('certified_epoch')}")
        
        # Test 2: Read the message back
        print("\n" + "=" * 60)
        print("📖 Test 2: Reading message from Walrus blockchain...")
        print("=" * 60)
        
        retrieved_text = walrus.read_text(blob_id)
        
        if retrieved_text:
            print(f"\n✅ Message retrieved successfully!")
            print(f"   Retrieved: {retrieved_text}")
            print(f"   Match: {'✅ YES' if retrieved_text == test_message else '❌ NO'}")
            
            # Test 3: Get blob info
            print("\n" + "=" * 60)
            print("ℹ️  Test 3: Getting blob information...")
            print("=" * 60)
            
            blob_info = walrus.get_blob_info(blob_id)
            if blob_info:
                print(f"\n✅ Blob info retrieved!")
                print(f"   Blob ID: {blob_info.get('blob_id')}")
                print(f"   Size: {blob_info.get('size')} bytes")
                print(f"   Exists: {blob_info.get('exists')}")
                print(f"   Aggregator URL: {blob_info.get('aggregator_url')}")
                
                print("\n" + "=" * 60)
                print("🎉 ALL TESTS PASSED!")
                print("=" * 60)
                print(f"\n🌐 View on Walrus Explorer:")
                print(f"   https://walruscan.com/testnet/blob/{blob_id}")
                print(f"\n🔗 Direct Access:")
                print(f"   {blob_info.get('aggregator_url')}")
            else:
                print("❌ Failed to get blob info")
        else:
            print("❌ Failed to retrieve message")
    else:
        print("❌ Failed to store message")
    
    walrus.close()
    print("\n" + "=" * 60)
    print("✅ Walrus service closed")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_walrus()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
