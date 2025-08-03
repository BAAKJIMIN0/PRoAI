import sys
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    input_data = json.loads(sys.argv[1])
    user_message = input_data.get("problem", "")

    prompt = "당신은 광고 및 커뮤니케이션 전략에 정통한 전문가입니다. 모든 답변을 한국어로, 친절하게 해주세요."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=1.0,
        max_tokens=1000
    )
    answer = response.choices[0].message.content.strip()
    print(answer)

if __name__ == "__main__":
    main()