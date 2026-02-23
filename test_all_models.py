import requests
import json
import time

def test_service(name, url, payload, model_name):
    print(f"\n🚀 正在测试 {name} 服务 ({url})...")
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ {name} 测试成功！(耗时: {duration:.2f}s)")
            if "embeddings" in url:
                print(f"📊 向量维度: {len(response.json()['data'][0]['embedding'])}")
            elif "chat" in url:
                print(f"💬 模型回复: {response.json()['choices'][0]['message']['content'][:50]}...")
            return True
        else:
            print(f"❌ {name} 失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ {name} 连接失败: {str(e)}")
        return False

def run_all_tests():
    services = [
        {
            "name": "嵌入模型 (Embedding)",
            "url": "http://localhost:8001/v1/embeddings",
            "model": "Qwen/Qwen3-Embedding-8B",
            "payload": {"model": "Qwen/Qwen3-Embedding-8B", "input": "你好，测试嵌入向量。"}
        },
        {
            "name": "对话模型 (Chat)",
            "url": "http://localhost:8002/v1/chat/completions",
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "payload": {
                "model": "Qwen/Qwen2.5-7B-Instruct", 
                "messages": [{"role": "user", "content": "你好，请自我介绍一下。"}]
            }
        }
    ]

    print("="*50)
    print("🌟 统一模型后端集成测试 🌟")
    print("="*50)

    for s in services:
        test_service(s["name"], s["url"], s["payload"], s["model"])

    print("\n" + "="*50)
    print("提示: OCR 服务请通过浏览器访问 http://localhost:8000 测试。")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
