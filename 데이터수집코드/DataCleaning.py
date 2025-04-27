import pandas as pd
import re

# 이모티콘 제거
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # 이모티콘
        u"\U0001F300-\U0001F5FF"  # 기호
        u"\U0001F680-\U0001F6FF"  # 탈 것
        u"\U0001F1E0-\U0001F1FF"  # 국기
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# 특수문자 제거 (한글, 영문, 숫자, 공백만 남김)
def remove_special_characters(text):
    return re.sub(r"[^가-힣a-zA-Z0-9\s]", "", text)

# 낱자 자음/모음 제거 (완성된 글자는 남기고 'ㄱ', 'ㅏ' 등만 제거)
def remove_korean_jamos(text):
    return re.sub(r"[ㄱ-ㅎㅏ-ㅣ]", "", text)

# 통합 정제 함수
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = remove_emojis(text)
    text = remove_korean_jamos(text)
    text = remove_special_characters(text)
    return text.strip()

# 엑셀 파일 불러오기 (파일명 바꿔도 됨)
input_path = "raw_data.xlsx"
output_path = "cleaned_data.xlsx"

# 엑셀 파일 읽기
df = pd.read_excel(input_path)

# '내용' 컬럼 정제하기
if "내용" in df.columns:
    df["정제된내용"] = df["내용"].apply(clean_text)
else:
    print("[!] '내용' 컬럼을 찾을 수 없습니다.")
    exit()

# 새 엑셀로 저장
df.to_excel(output_path, index=False)
print(f"[✔] 정제 완료! 저장 위치: {output_path}")
