import os
from pymongo import MongoClient  # MongoDB 연동
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# 현재 디렉토리 기준 설정
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/test')

# MongoDB에서 데이터 불러오기
mongo_client = MongoClient("mongodb://smim:1q2w3e4r@ubuntu-server.tplinkdns.com:27017") #mongodb://localhost:27017/ # mongodb://smim:1q2w3e4r@ubuntu-server.tplinkdns.com:27017
db = mongo_client["pro"]
collection = db["pro"]
mongo_data = list(collection.find({}))  # 모든 document 가져오기

# HuggingFace 임베딩 모델 지정 (로컬 실행, 무료)
embedding_model = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask"
)
'''
jhgan/ko-sroberta-multitask (다목적 한국어 임베딩, 많이 쓰임)

BM-K/KoSimCSE-roberta-multitask (문장 유사도 특화)

sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (멀티랭 지원, 가볍고 빠름)
'''

# 리스트 초기화
client = []
background = []
solution = []
target = []
concept = []
content = []
assistance = []


# A 방식: 하나의 문서로 통합 저장
# result_a = []
# for doc in mongo_data:
#     # 필드들을 안전하게 가져오고 공백 제거
#     client_content = doc.get("client", "").strip()
#     background_content = doc.get("background", "").strip()
#     solution_content = doc.get("solution", "").strip()
#     target_content = doc.get("target", "").strip()
#     concept_content = doc.get("concept", "").strip()
#     content_content = doc.get("content", "").strip()
#     assistance_content = doc.get("assistance", "").strip()
    
#     # 모든 내용이 비어있지 않은 경우에만 문서 생성
#     if any([client_content, background_content, solution_content, target_content, concept_content, content_content, assistance_content]):
#         page_content = (
#             f"클라이언트: {client_content}\n"
#             f"문제 배경: {background_content}\n"
#             f"해결 과제: {solution_content}\n"
#             f"주 타겟: {target_content}\n"
#             f"메인 커뮤니케이션 컨셉: {concept_content}\n"
#             f"주요 내용: {content_content}\n"
#             f"추가 분석: {assistance_content}"
#         )
#         result_a.append(
#             Document(   
#                 page_content=page_content,
#                 metadata={"idx": str(doc.get("_id", "no_id"))}
#             )
#         )
        
# if result_a:
#     vectordb_a = Chroma.from_documents(
#         documents=result_a,
#         embedding=embedding_model,
#         persist_directory=CHROMA_PERSIST_DIR,
#         collection_name="RAG_A",
#     )
#     vectordb_a.persist()
#     print("벡터 DB A가 저장되었습니다.")
# else:
#     print("벡터화할 유효한 데이터가 없습니다. (A 방식)")

### **B 방식: 항목 별로 문서 저장**
result_b = []
sections = ["client", "background", "solution", "target", "concept", "content", "assistance"]

for doc in mongo_data:
    for section in sections:
        section_content = doc.get(section, "").strip()
        # 빈 문자열이 아닌 경우에만 추가
        if section_content:
            result_b.append(
                Document(
                    page_content=section_content,
                    metadata={
                        "idx": str(doc.get("_id", "no_id")),
                        "section": section
                    }
                )
            )

if result_b:
    vectordb_b = Chroma.from_documents(
        documents=result_b,
        embedding=embedding_model,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name="RAG_B",
    )
    vectordb_b.persist()
    print("벡터 DB B가 저장되었습니다.")
else:
    print("벡터화할 유효한 데이터가 없습니다. (B 방식)")
