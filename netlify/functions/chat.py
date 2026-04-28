import os
import json
import requests

# Netlify 自动读取环境变量，不用 load_dotenv()
API_KEY = os.getenv("ZHIPU_API_KEY")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"

# Netlify 函数固定入口
def handler(event, context):
    # 获取前端传的参数
    prompt = event["queryStringParameters"]["q"]
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 请求数据
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是简约风格的个人博客写作助手"},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.7
    }

    # 流式响应生成器
    def generate_stream():
        with requests.post(URL, headers=headers, json=data, stream=True) as res:
            for line in res.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    chunk = line.replace("data: ", "")
                    if chunk == "[DONE]":
                        break
                    yield f"data:{chunk}\n\n"

    # 返回流式响应
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        },
        "body": "".join(generate_stream())
    }