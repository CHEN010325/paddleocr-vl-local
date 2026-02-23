import os
import httpx
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="RAG Rerank API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 环境变量配置
# vLLM 服务地址 (Docker 内部网络使用服务名 reranker-server)
# 默认指向 docker-compose 中的 reranker-server 服务
RERANKER_SERVICE_URL = os.getenv("RERANKER_SERVICE_URL", "http://reranker-server:8000/v1/score")
RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME", "Qwen/Qwen3-Reranker-0.6B")

# Qwen3-Reranker Prompt 模板
RERANK_PREFIX = '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
RERANK_SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
RERANK_INSTRUCTION = "Given a web search query, retrieve relevant passages that answer the query"

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    top_k: Optional[int] = None

class RerankResultItem(BaseModel):
    index: int
    score: float
    document: str

class RerankResponse(BaseModel):
    results: List[RerankResultItem]

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "RAG Rerank API"}

@app.post("/api/rerank", response_model=RerankResponse)
async def rerank(request: RerankRequest):
    """
    Rerank documents using Qwen3-Reranker model.
    Automatically handles prompt formatting for RAG.
    """
    try:
        if not request.documents:
            return {"results": []}

        # 1. 构造带指令的输入
        text_1_list = []
        text_2_list = []
        
        for doc in request.documents:
            # 格式化 Query 和 Document
            query_part = f"{RERANK_PREFIX}<Instruct>: {RERANK_INSTRUCTION}\n<Query>: {request.query}\n"
            doc_part = f"<Document>: {doc}{RERANK_SUFFIX}"
            
            text_1_list.append(query_part)
            text_2_list.append(doc_part)
            
        # 2. 构造 vLLM 请求 Payload
        payload = {
            "model": RERANKER_MODEL_NAME,
            "text_1": text_1_list,
            "text_2": text_2_list
        }
        
        # 3. 发送请求给 Reranker 服务
        print(f"Sending request to Reranker Service at {RERANKER_SERVICE_URL}...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(RERANKER_SERVICE_URL, json=payload)
            
            if resp.status_code != 200:
                print(f"Reranker Error: {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=f"Reranker service error: {resp.text}")
                
            result = resp.json()
            
        scores_data = result.get('data', [])
        
        # 4. 解析结果并排序
        reranked_results = []
        for item in scores_data:
            idx = item.get('index')
            score = item.get('score')
            if idx is not None and idx < len(request.documents):
                reranked_results.append({
                    "index": idx,
                    "score": score,
                    "document": request.documents[idx]
                })
        
        # 按分数降序排序
        reranked_results.sort(key=lambda x: x["score"], reverse=True)
        
        # 如果指定了 top_k，截取前 K 个
        if request.top_k:
            reranked_results = reranked_results[:request.top_k]
            
        return {"results": reranked_results}
        
    except Exception as e:
        print(f"Error in rerank api: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"Starting Rerank API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
