import json
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key="")

input_path = "finetune_data_300.jsonl"
output_path = "tone_tuning_data.jsonl"

tones = {
    "언어유희형": "재미있고 언어적 유머를 살린 말투로",
    "감성유발형": "감정적이고 따뜻하게 마음을 울리는 말투로",
    "문제해결형": "논리적이고 실용적인 해결 중심의 말투로",
    "정보전달형": "사실적이고 객관적인 설명 중심의 말투로",
    "공감형": "사람들에게 공감과 위로를 주는 말투로"
}

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        data = json.loads(line)
        messages = data.get("messages", [])
        assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
        if not assistant_msg:
            continue

        for tone, desc in tones.items():
            prompt = f"다음 문장을 {desc} 다시 써줘:\n\n{assistant_msg}"
            response = client.chat.completions.create(
                model="gpt-4o",  # 또는 gpt-4o / gpt-4-turbo / gemini-1.5-pro 등
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            rewritten = response.choices[0].message.content.strip()

            out = {
                "input_text": f"문장: {assistant_msg}, tone: {tone}",
                "output_text": rewritten
            }
            outfile.write(json.dumps(out, ensure_ascii=False) + "\n")

print("✅ tone_tuning_data.jsonl 생성 완료 (5톤 전체 리라이트)")
