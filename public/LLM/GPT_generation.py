# env파일 설정
# langchain, openai, chromadb 설치 필요
import os,sys
from dotenv import load_dotenv
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.")
openai.api_key = OPENAI_API_KEY

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/chroma_persist')
CHROMA_COLLECTION_NAME = "RAG_test"

def create_prompt(query):
    # 질문과 가장 관련있는 본문 3개를 가져옴
    result = query_vectordb(query, use_retriever=True)
    print(result[0].page_content)
    print(result[1].page_content)
    print(result[2].page_content)
    
    system_message = f"""
        ################################################
        DB에 저장된 문서와 관련된 답변 3개
        Documents:
        doc1: """ + result[0].page_content + """
        doc2: """ + result[1].page_content + """
        doc3: """ + result[2].page_content + """
        
        ################################################
        
    """

    user_content = f"""
        User question: "{str(query)}". 
        Answer the question based on the documents above.
        If the answer is not in the documents, say "I don't know".
        If the answer is in the documents, provide the answer and the document name.
        
        Answer in Korean.
        Give at least three different variations of the answer in different formats.
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_content},
    ]
    return messages

def query_vectordb(query: str, use_retriever: bool = False):
    from pprint import pprint

    # vecotordb 로드
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
    try:
        print("\nuser: ", end="")
        user_content = sys.stdin.read()
    except (KeyboardInterrupt, EOFError):
        print("\n입력 종료")
        break

    if not user_content:
        print("입력 내용이 없습니다. 다시 입력해 주세요.")
        continue
    
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

    print(f"\nGPT : {assistant_content}")
