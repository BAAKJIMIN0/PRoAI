import sys
import json
import os,sys
from dotenv import load_dotenv
import openai
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.")
openai.api_key = OPENAI_API_KEY

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/test')
#CHROMA_COLLECTION_NAME = "RAG_test"

messages = []
user_content = []

def create_prompt(query: dict):
    # 각 질문과 가장 관련있는 본문 3개를 가져옴
    problem = query_vectordb(query["background"], use_retriever=True, purpose="background")
    client = query_vectordb(query["target"], use_retriever=True, purpose="target")
    needs = query_vectordb(query["solution"], use_retriever=True, purpose="solution")
    trend = query_vectordb(query["assistance"], use_retriever=True, purpose="assistance")
    
    result = problem + client + needs + trend

    # result가 비어있으면 안내 메시지 반환
    if not result:
        docs_text = ""
        system_message = "DB에서 관련 문서를 찾지 못했습니다. 질문에 직접 답변해 주세요."
    else:
        # 각 문서의 내용을 추출하여 문자열로 연결
        docs_text = "\n\n".join([doc.page_content for doc in result])
        system_message = f"""
        ################################################
        DB에 저장된 문서와 관련된 답변
        Documents: 
        {docs_text}
        ################################################
        """

    user_content = f"""
        User question: "{str(query)}". 
        Answer the question based on the DB-RAG documents above.
        If it is in the document, actively refer to the document and create an answer. 
        If it is not in the document, inform the user that it is not in the document and create an appropriate answer.
        Answer in Korean.
        Finally, refer to the document to create the most appropriate Comunication concept phrase.
        Give at least three different variations of the answer in different formats.
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_content},
    ]
    return messages

def query_vectordb(query: str, purpose: str, use_retriever: bool = False):
    # vecotordb 로드
    vectordb_A = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name="RAG_A",
    )
    
    vectordb_B = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name="RAG_B",
    )

    # 벡터 DB에서 질문과 가장 관련있는 본문 3개를 가져옴
    if use_retriever:
        retriever = vectordb_B.as_retriever(search_kwargs={"k": 3}, filter={"section":{purpose}})
        top_docs = retriever.get_relevant_documents(query)
        
        # idx를 기준으로 필터링
        idx_list = [doc.metadata["idx"] for doc in top_docs]
        all_docs = vectordb_A.similarity_search(query, k=5)  # 충분히 가져오기
        top_docs = [doc for doc in all_docs if doc.metadata.get("idx") in idx_list]
        
        '''retriever = vectordb_A.as_retriever(
            search_kwargs={"k": 3},
            filter={"idx":{"$in":idx_list}}
        )
        top_docs = retriever.get_relevant_documents(query)'''
        
    else:
        top_docs = vectordb_A.similarity_search(query, k=3)
    return top_docs

def generate_answer(theme, problem, task, info, target, keyword):
    # 입력값이 None일 경우 빈 문자열로 처리
    theme = theme or ""
    problem = problem or ""
    task = task or ""
    info = info or ""
    target = target or ""
    keyword = keyword or ""
    # 한 줄로 출력
    return f"테마: {theme} | 문제: {problem} | 작업: {task} | 정보: {info} | 대상: {target} | 키워드: {keyword}"

if __name__ == "__main__":
    input_json = sys.argv[1]
    data = json.loads(input_json)

    # user_content는 문제정의, 타겟설정, 니즈파악, 트렌드 분석 순
    problem_text = data.get('problem', '')
    client_text = data.get('target', '')
    needs_text = data.get('task', '')
    trend_text = data.get('info', '')

    # create_prompt에 맞게 매핑
    messages = create_prompt(
        {
            "background": problem_text,
            "target": client_text,
            "solution": needs_text,
            "assistance": trend_text
        }
    )

    # GPT 출력
    completion = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0125:personal::BWh2RT51",
        messages=messages,
        temperature=1.0,
        max_tokens=1000
    )
    assistant_content = completion.choices[0].message["content"].strip()

    print(assistant_content)
