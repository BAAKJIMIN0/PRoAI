
# Hugging Face에 있는 적절한 오픈소스 AI Model을 조사한 후 로드하고 미세 조정하기
+ ## 모델은 한국어에 미숙하기에 한국 LLM 리더보드에 있는 모델 로드
### 1. 카카오의 'kakaocorp/kanana-nano-2.1b-instruct' 모델 선택
![image](https://github.com/user-attachments/assets/3ceaab27-3a6f-4265-9909-b3e7b66848f2)
출처 https://huggingface.co/kakaocorp/kanana-nano-2.1b-instruct

+ ## kanana는 2.1b 개수의 프롬프트를 학습시킨 작은 모델로 크기 대비 효율이 좋다

----

```
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from transformers import AutoModel, AutoTokenizer
from transformers import AutoModelForCausalLM
import torch

```
### 필요한 경우 미세 튜닝을 위해 데이터셋의 작은 부분 집합을 만들어 미세 튜닝 작업 시간을 줄일 수 있다
```
model_name = "kakaocorp/kanana-nano-2.1b-instruct" # "-instruct" 지시에 따르도록 파인튜닝이 된 모델
#model_name = "kakaocorp/kanana-nano-2.1b-base" # base 모델로도 지시 훈련 가능
#model_name = "microsoft/Phi-4-mini-instruct" # MIT 라이센스라서 상업적 사용 가능

```
### 모델 로드와 토크나이저 생성
```

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    # torch_dtype="auto", # Phi-4-mini 모델
    trust_remote_code=True,
)   # .to("cuda") nvidia GPU에서만 지원되는 torch_dtype="bfloat16" 사용 가능

tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token # <|eot_id|> 128009

```
### 질문 작성
```

messages = [
    {"role": "system", "content": "You are a helpful AI assistant developed by Kakao."},
    {"role": "user", "content": "1 더하기 1 은?"},
    {"role": "assistant", "content":" 귀요미 >_<"},
    
    {"role": "system", "content": "You are a helpful AI assistant developed by Kakao."},
    {"role": "user", "content": "동아대학교의 주소를 알려줘"},
    {"role": "assistant", "content":"동아대학교 승학 캠퍼스의 주소는 부산광역시 사하구 낙동대로550번길 37 입니다."}
]

```
### 질문지 토큰화 결과 출력
```

tokens = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

print(tokens)
```

## 결과 : kanana 모델은 작은 크기로 빠른 속도로 정상 작동

### 2. 'SEOKDONG/llama3.1_korean_v1.1_sft_by_aidx' 모델 선택
<https://huggingface.co/spaces/upstage/open-ko-llm-leaderboard>

-----


```
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from transformers import AutoModel, AutoTokenizer
from transformers import TrainingArguments, Trainer  # 하이퍼 파라미터 훈련
import numpy as np
import evaluate
import torch

tokenizer = AutoTokenizer.from_pretrained("SEOKDONG/llama3.1_korean_v1.1_sft_by_aidx")
model = AutoModel.from_pretrained("SEOKDONG/llama3.1_korean_v1.1_sft_by_aidx")

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
```
### 필요한 경우 미세 튜닝을 위해 데이터셋의 작은 부분 집합을 만들어 미세 튜닝 작업 시간을 줄일 수 있다
```
small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000))
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(1000))
```
### 훈련에서 체크포인트(checkpoints)를 저장할 위치를 지정
```
training_args = TrainingArguments(output_dir="test_trainer")
```
### Evaluate 라이브러리는 evaluate.load 함수로 로드할 수 있는 간단한 accuracy함수 제공
```
metric = evaluate.load("accuracy")
```
### 예측을 compute에 전달하기 전에 예측을 로짓으로 변환(모든 Transformers 모델은 로짓으로 반환해야함)
```
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)
```
### eval_strategy 파라미터를 지정하여 각 에폭이 끝날 때 평가 지표를 확인    
```
training_args = TrainingArguments(output_dir="test_trainer", eval_strategy="epoch")
```
### 모델, 훈련 인수, 훈련 및 테스트 데이터셋, 평가 함수가 포함된 Trainer 객체를 만듬
```
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_eval_dataset,
    compute_metrics=compute_metrics,
)
```
### train()을 호출하여 모델을 미세 튜닝
```
trainer.train()

```
### 학습된 모델과 질의응답
```
input_text =  """ 「국민건강보험법」제44조, 「국민건강보험법 시행령」제19조,「약관의 규제에 관한 법률」제5조, 「상법」제54조 참조 판단 해줘""" + " 답변:"
inputs = tokenizer(input_text, return_tensors="pt")

with torch.no_grad():
    outputs = model.generate(**inputs, max_length=1024,  temperature=0.5, do_sample=True, repetition_penalty=1.15)

result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(result)
```

## 결과 : 라마 모델은 용량이 비교적 크고 모델 로드 후 프롬프트가 나오지 않는 문제 발생, 오류 수정중에 있음

