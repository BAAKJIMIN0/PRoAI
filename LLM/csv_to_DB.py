import pandas as pd
from pymongo import MongoClient

# CSV 파일 경로

# MongoDB 연결 (localhost:27017)
mongo_client = MongoClient("mongodb://mskim:1q2w3e4r@ubuntu-server.tplinkdns.com:27017") # mongodb://localhost:27017/ | mongodb://mskim:1q2w3e4r@ubuntu-server.tplinkdns.com:27017
db = mongo_client["pro"]   # 데이터베이스 이름
collection = db["pro"]     # 컬렉션 이름

# CSV 파일 읽기
df1 = pd.read_csv(
    r"C:\Users\gonza\Desktop\슈퍼히어로 컨셉 데이타\공익 데이터.csv",
    quotechar='"',
    engine="python",
    encoding="utf-8",
    on_bad_lines="skip"  # 문제 있는 라인 무시
)

df2 = pd.read_csv(
    r"C:\Users\gonza\Desktop\슈퍼히어로 컨셉 데이타\기업1 데이터.csv",
    quotechar='"',
    engine="python",
    encoding="utf-8",
    on_bad_lines="skip"  # 문제 있는 라인 무시
)

df3 = pd.read_csv(
    r"C:\Users\gonza\Desktop\슈퍼히어로 컨셉 데이타\기업2 데이터.csv",
    quotechar='"',
    engine="python",
    encoding="utf-8",
    on_bad_lines="skip"  # 문제 있는 라인 무시
)

df4 = pd.read_csv(
    r"C:\Users\gonza\Desktop\슈퍼히어로 컨셉 데이타\비정제1 데이터.csv",
    quotechar='"',
    engine="python",
    encoding="utf-8",
    on_bad_lines="skip"  # 문제 있는 라인 무시
)

# 한글 컬럼명을 영어로 매핑
column_mapping = {
    "사례 번호": "case_id",
    "클라이언트": "client",
    "문제 배경": "background",
    "해결 과제": "solution",
    "주 타겟": "target",
    "커뮤니케이션 컨셉": "concept",
    "주요 실행 내용": "content",
    "추가 분석": "assistance"
}

df1.rename(columns=column_mapping, inplace=True)
df2.rename(columns=column_mapping, inplace=True)
df3.rename(columns=column_mapping, inplace=True)
df4.rename(columns=column_mapping, inplace=True)

# MongoDB에 삽입할 문서 리스트 변환
records1 = df1.to_dict(orient="records")
records2 = df2.to_dict(orient="records")
records3 = df3.to_dict(orient="records")
records4 = df4.to_dict(orient="records")

all_records = records1 + records2 + records3 + records4

# MongoDB에 삽입 (중복 방지를 위해 전체 삭제 후 삽입 가능)
collection.delete_many({})   # 기존 데이터 초기화 
collection.insert_many(all_records)

print(f"{len(all_records)}개의 문서가 MongoDB에 저장되었습니다.")
