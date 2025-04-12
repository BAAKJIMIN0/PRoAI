
# Hugging Face에 있는 적절한 오픈소스 AI Model을 조사한 후 로드하고 미세 조정하기
+ ### base 모델은 한국어에 미숙하기에 한국 LLM 리더보드에 있는 모델 로드
+ ### 그 중 'SEOKDONG/llama3.1_korean_v1.1_sft_by_aidx' 모델 선택
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

