import os
import openai
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader, UnstructuredMarkdownLoader, NotebookLoader
from SimpleDocxLoader import SimpleDocxLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# 1. OpenAI API 키 환경변수에서 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.")
openai.api_key = OPENAI_API_KEY

# 2. 경로 설정 (현재 파일 기준 절대 경로)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/chroma_persist')
CHROMA_COLLECTION_NAME = "RAG_test"

# 3. 확장자별 로더 매핑
LOADER_DICT = {
    "pdf": PyPDFLoader,
    "txt": TextLoader,
    "md": UnstructuredMarkdownLoader,
    "ipynb": NotebookLoader,
    "docx": SimpleDocxLoader,
}

loader_pdf = LOADER_DICT.get('pdf')
loader_docx = LOADER_DICT.get('docx')
loader_cls = [loader_pdf,loader_docx]
for loader in loader_cls:
    if loader is not None:
        print(f"'{loader}' 파일을 로드할 수 있는 로더가 있습니다.")

# 4. DirectoryLoader로 폴더 내 PDF 불러오기
data_dir = os.path.join(CUR_DIR, './db/chroma_persist')  
loader_pdf = DirectoryLoader(data_dir, glob="*.pdf", loader_cls=loader_pdf)
loader_docx = DirectoryLoader(data_dir, glob="*.docx", loader_cls=loader_docx)
loaders = [loader_pdf,loader_docx]

# 5. 문서 로드
docs = []
for loader in loaders:
    docs.extend(loader.load())
    
print(docs[0])
print('문서의 개수 :', len(docs), end="\n\n")

# 6. 텍스트 분할
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(docs)
print(texts[0:5])
print('문서의 조각 수 :', len(texts), end="\n\n")

# 7. 벡터 DB 생성 및 저장
vectordb = Chroma.from_documents(
    documents=texts,
    embedding=OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_DIR,
    collection_name=CHROMA_COLLECTION_NAME,
)

# 8. 벡터 DB 영구 저장
vectordb.persist()
print(f"벡터 DB가 '{CHROMA_PERSIST_DIR}'에 저장되었습니다.")
