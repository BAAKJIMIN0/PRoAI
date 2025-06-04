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

# 학습용 파일 업로드
train_file = client.files.create(
    file=open("finetune_data_300.jsonl", "rb"),
    purpose="fine-tune"
)
print(f"학습 파일 업로드 완료! 파일 ID: {train_file.id}")

# 파인튜닝 작업 생성
job = client.fine_tuning.jobs.create(
    training_file=train_file.id,
    model="gpt-3.5-turbo"
)
job_id = job.id
print(f"파인튜닝 시작! 작업 ID: {job_id}")

# 학습이 완료될 때까지 대기하면서 상태 출력
print("Fine-tuning in progress...\n")
while True:
    status = client.fine_tuning.jobs.retrieve(job_id)
    print(f"현재 상태: {status.status}, 완료 단계: {status.finished_at}, 생성된 모델: {status.fine_tuned_model}")
    if status.status == "succeeded":
        print("\nFine-tuning complete!")
        break
    elif status.status == "failed":
        raise RuntimeError("Fine-tuning failed.")
    time.sleep(5)

# 학습 완료된 모델 ID 출력
fine_tuned_model = status.fine_tuned_model
print(f"\nFine-tuned 모델 ID: {fine_tuned_model}")

# 사용자 프롬프트 입력 대기
prompt = input("\nuser: ")

# 프롬프트로 응답 생성
response = client.chat.completions.create(
    model=fine_tuned_model,
    messages=[{"role": "user", "content": prompt}]
)

# 응답 출력
print("GPT:", response.choices[0].message.content)
