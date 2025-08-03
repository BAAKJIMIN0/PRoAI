import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

# OpenAI 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

while True:
    prompt = input("\nuser: ")

    # 프롬프트로 응답 생성
    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal::BWh2RT51",
        messages=[{"role": "user", "content": prompt}]
    )

    # 응답 출력
    print("GPT:", response.choices[0].message.content)