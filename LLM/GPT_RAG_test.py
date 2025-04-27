import os
import openai
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader, UnstructuredMarkdownLoader, NotebookLoader
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
}

file_ext = 'pdf'
loader_cls = LOADER_DICT.get(file_ext)
if loader_cls is None:
    raise ValueError(f"지원하지 않는 파일형식입니다: {file_ext}")

# 4. DirectoryLoader로 폴더 내 PDF 불러오기
data_dir = os.path.join(CUR_DIR, './db/chroma_persist')  
loader = DirectoryLoader(data_dir, glob="*.pdf", loader_cls=loader_cls)

# 5. 문서 로드
docs = loader.load()
print(docs[0])
print('문서의 개수 :', len(docs), end="\n\n")

# 6. 텍스트 분할
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(docs)
print(texts[0])
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

def create_prompt(query):
    # 질문과 가장 관련있는 본문 3개를 가져옴
    result = query_vectordb(query, use_retriever=True)
    print(result[0].page_content)
    print(result[1].page_content)
    print(result[2].page_content)
    
    system_message = f"""
        ################################################
        DB에 저장된 문서와 관련된 답변 3개개
        Documents:
        doc1: """ + result[0].page_content + """
        doc2: """ + result[1].page_content + """
        doc3: """ + result[2].page_content + """
        
        ################################################
        
    """

    user_content = f"""User question: "{str(query)}". """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_content},
    ]
    return messages

def query_vectordb(query: str, use_retriever: bool = False):
    from pprint import pprint

    # vecotordb 로드드
    vectordb = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
    )

    # 벡터 DB에서 질문과 가장 관련있는 본문 3개를 가져옴
    if use_retriever:
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        top_docs = retriever.get_relevant_documents(query)
    else:
        top_docs = vectordb.similarity_search(query, k=3)

    pprint(top_docs)
    return top_docs

messages = []
while True:
    user_content = input("user : ")
    
    #messages.append({"role": "user", "content": f"{user_content}"})
    # 사용자 입력
    messages = create_prompt(user_content)

    # GPT 출력
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.4,
        max_tokens=500
    )
    assistant_content = completion.choices[0].message["content"].strip()

    messages.append({"role": "assistant", "content": f"{assistant_content}"})

    print(f"GPT : {assistant_content}")
