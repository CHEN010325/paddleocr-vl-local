import requests
import json
import time

# API 配置
API_URL = "http://localhost:8001/v1/score"
MODEL_NAME = "Qwen/Qwen3-Reranker-0.6B"

# RAG 指令模板
PREFIX = '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
INSTRUCTION = "Given a web search query, retrieve relevant passages that answer the query"

def format_input(query, doc):
    query_part = f"{PREFIX}<Instruct>: {INSTRUCTION}\n<Query>: {query}\n"
    doc_part = f"<Document>: {doc}{SUFFIX}"
    return query_part, doc_part

def test_reranker():
    print(f"Testing Reranker API at {API_URL}...")
    
    # 测试数据
    query = "What is the capital of China?"
    documents = [
        "Beijing is the capital of China.",           # 相关
        "Shanghai is a major city in China.",         # 部分相关
        "Tokyo is the capital of Japan.",             # 不相关
        "Paris is the capital of France.",            # 不相关
        "The quick brown fox jumps over the lazy dog." # 完全不相关
    ]
    
    # 构造带指令的输入
    text_1_list = []
    text_2_list = []
    
    for doc in documents:
        q_fmt, d_fmt = format_input(query, doc)
        text_1_list.append(q_fmt)
        text_2_list.append(d_fmt)
    
    # 注意：Qwen3-Reranker 在 vLLM 中支持批量输入
    # text_1 和 text_2 必须长度一致，一一对应
    payload = {
        "model": MODEL_NAME,
        "text_1": text_1_list,
        "text_2": text_2_list
    }
    
    try:
        print("Sending request...", flush=True)
        start_time = time.time()
        response = requests.post(API_URL, json=payload)
        end_time = time.time()
        print("Request completed.", flush=True)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ API Call Successful!")
            print(f"Time taken: {end_time - start_time:.4f} seconds")
            
            print("\nQuery:", query)
            print("-" * 80)
            print(f"{'Score':<10} | {'Status':<12} | {'Document'}")
            print("-" * 80)
            
            scores = result.get('data', [])
            
            # Create results list
            results_with_docs = []
            for item in scores:
                idx = item.get('index')
                score = item.get('score')
                if idx is not None and idx < len(documents):
                    status = "✅ Keep" if score >= 0.4 else "❌ Filter"
                    results_with_docs.append((score, status, documents[idx]))
            
            # Sort by score descending
            results_with_docs.sort(key=lambda x: x[0], reverse=True)
            
            for score, status, doc in results_with_docs:
                print(f"{score:.6f} | {status}   | {doc}")
                
            print("-" * 80)
            
        else:
            print(f"\n❌ API Call Failed with status code: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    test_reranker()
