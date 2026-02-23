import requests
import json

# 新的 Rerank 接口地址
API_URL = "http://localhost:8002/api/rerank"

def test_new_api():
    print(f"Testing New Rerank API at {API_URL}...")
    
    query = "What is the capital of China?"
    documents = [
        "Beijing is the capital of China.",
        "Shanghai is a major city in China.",
        "Tokyo is the capital of Japan.",
        "Paris is the capital of France.",
        "The quick brown fox jumps over the lazy dog."
    ]
    
    # 新接口只需要传 query 和 documents，不用关心 Prompt
    payload = {
        "query": query,
        "documents": documents,
        "top_k": 3  # 可选：只要前3个
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ API Call Successful!")
            
            print("\nQuery:", query)
            print("-" * 80)
            print(f"{'Score':<10} | {'Document'}")
            print("-" * 80)
            
            for item in result["results"]:
                score = item["score"]
                doc = item["document"]
                print(f"{score:.6f} | {doc}")
                
            print("-" * 80)
            print("\nFull JSON Response:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"\n❌ API Call Failed with status code: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    test_new_api()
