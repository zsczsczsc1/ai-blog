import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI()

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("ZHIPU_API_KEY")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"

# ------------------- AI 流式接口 -------------------
def stream_answer(prompt: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是简约风格的个人博客写作助手"},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.7
    }

    with requests.post(URL, headers=headers, json=data, stream=True) as res:
        for line in res.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                chunk = line.replace("data: ", "")
                if chunk == "[DONE]":
                    break
                yield f"data:{chunk}\n\n"

@app.get("/api/ai/stream")
def ai_stream(q: str):
    return StreamingResponse(
        stream_answer(q),
        media_type="text/event-stream"
    )

# ------------------- 文章存储（Vercel 内存版） -------------------
articles = []

class ArticleSave(BaseModel):
    title: str
    content: str

@app.post("/api/articles")
def save_article(article: ArticleSave):
    filename = f"{article.title}_{int(time.time())}.md"
    new_article = {
        "filename": filename,
        "title": article.title,
        "content": article.content,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    articles.append(new_article)
    return {"status": "success", "filename": filename}

@app.get("/api/articles")
def list_articles():
    return {"articles": articles}

@app.get("/api/articles/{filename}")
def get_article(filename: str):
    for a in articles:
        if a["filename"] == filename:
            return {"title": a["title"], "content": a["content"]}
    return {"status": "error", "message": "文章不存在"}