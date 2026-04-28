import os
import json
import requests

# 读取密钥
API_KEY = os.getenv("ZHIPU_API_KEY")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"

# Netlify 固定函数入口
def handler(event, context):
    # 获取用户输入
    prompt = event["queryStringParameters"]["q"]
    
    # 请求智谱AI
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
        "temperature": 0.7
    }

    # 普通请求（非流式，Netlify 100%支持）
    response = requests.post(URL, headers=headers, json=data)
    result = response.json()
    
    # 返回结果
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(result)
    }