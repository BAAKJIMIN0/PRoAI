import os
import openai
from dotenv import load_dotenv
from pymongo import MongoClient  # MongoDB 연동
from langchain.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader, UnstructuredMarkdownLoader, NotebookLoader
from SimpleDocxLoader import SimpleDocxLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

# 환경변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.")
openai.api_key = OPENAI_API_KEY

# 현재 디렉토리 기준 설정
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/test')
CHROMA_COLLECTION_NAME = "RAG_A"

# MongoDB에서 데이터 불러오기
mongo_client = MongoClient("mongodb://smim:1q2w3e4r@ubuntu-server.tplinkdns.com:27017")
db = mongo_client["proai"]
collection = db["proai"]
mongo_data = list(collection.find({}))  # 모든 document 가져오기

# 리스트 초기화
client = []
background = []
solution = []
target = []
concept = []
content = []
assistance = []

# MongoDB에서 값 추출
for doc in mongo_data:
    client.append(doc.get("client", ""))
    background.append(doc.get("background", ""))
    solution.append(doc.get("solution", ""))
    target.append(doc.get("target", ""))
    concept.append(doc.get("concept", ""))
    content.append(doc.get("content", ""))
    assistance.append(doc.get("assistance", ""))

sections = ["client", "background", "solution", "target", "concept", "content", "assistance"]

# A 방식: 하나의 문서로 통합 저장
result_a = []
for i in range(len(client)):
    result_a.append(
        Document(
            page_content=f"클라이언트: {client[i]}\n"
                         f"문제 배경: {background[i]}\n"
                         f"해결 과제: {solution[i]}\n"
                         f"주 타겟: {target[i]}\n"
                         f"메인 커뮤니케이션 컨셉: {concept[i]}\n"
                         f"주요 내용: {content[i]}\n"
                         f"추가 분석: {assistance[i]}",
            metadata={"idx": i}
        )
    )

vectordb_a = Chroma.from_documents(
    documents=result_a,
    embedding=OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_DIR,
    collection_name="RAG_A",
)
vectordb_a.persist()
print("벡터 DB A가 저장되었습니다.")

# B 방식: 항목 별로 문서 저장
result_b = []
for i in range(len(client)):
    for section in sections:
        section_content = eval(section)[i]
        result_b.append(
            Document(
                page_content=section_content,
                metadata={
                    "idx": i,
                    "section": section
                }
            )
        )

vectordb_b = Chroma.from_documents(
    documents=result_b,
    embedding=OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_DIR,
    collection_name="RAG_B",
)
vectordb_b.persist()
print("벡터 DB B가 저장되었습니다.")
