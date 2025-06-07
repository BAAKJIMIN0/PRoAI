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
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/test')
#CHROMA_COLLECTION_NAME = "RAG_test"

def create_prompt(query: dict):
    # 각 질문과 가장 관련있는 본문 3개를 가져옴
    problem = query_vectordb(query["background"], use_retriever=True, purpose="background")
    client = query_vectordb(query["target"], use_retriever=True, purpose="target")
    needs = query_vectordb(query["solution"], use_retriever=True, purpose="solution")
    trend = query_vectordb(query["assistance"], use_retriever=True, purpose="assistance")
    
    result = problem + client + needs + trend

    # 결과 출력
    print(result[0].page_content)

    # 각 문서의 내용을 추출하여 문자열로 연결
    docs_text = "\n\n".join([doc.page_content for doc in result])
    
    # system_message 구성
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
    from pprint import pprint

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
        print("\nuse retriever\n")
        retriever = vectordb_B.as_retriever(search_kwargs={"k": 3}, filter={"section":{purpose}})
        top_docs = retriever.get_relevant_documents(query)
        
        # idx를 기준으로 필터링
        idx_list = [doc.metadata["idx"] for doc in top_docs]
        print(f"\nidx_list: {idx_list}\n")
        all_docs = vectordb_A.similarity_search(query, k=5)  # 충분히 가져오기
        top_docs = [doc for doc in all_docs if doc.metadata.get("idx") in idx_list]
        
        '''retriever = vectordb_A.as_retriever(
            search_kwargs={"k": 3},
            filter={"idx":{"$in":idx_list}}
        )
        top_docs = retriever.get_relevant_documents(query)'''
        
    else:
        print("\nuse similarity search\n")
        
        top_docs = vectordb_A.similarity_search(query, k=3)

    pprint(top_docs)
    return top_docs


messages = []
user_content = []

while True:
    try: 
        print("문제 정의: ", end="")
        problem = sys.stdin.read()
        user_content.append(problem.strip())

        print("\n타겟 설정: ", end="")
        client = sys.stdin.read()
        user_content.append(client.strip())

        print("\n니즈 파악: ", end="")
        needs = sys.stdin.read()
        user_content.append(needs.strip())

        print("\n트렌드 분석: ", end="")
        trend = sys.stdin.read()
        user_content.append(trend.strip())

    except (KeyboardInterrupt, EOFError):
        print("\n입력 종료")
        break

    if not user_content:
        print("입력 내용이 없습니다. 다시 입력해 주세요.")
        continue
    
    print("\n입력 내용" + f"\n{user_content}\n")
    
    # user_content는 문제정의, 타겟설정, 니즈파악, 트렌드 분석 순
    if len(user_content) != 4:
        raise ValueError("user_content는 [문제정의, 타겟설정, 니즈파악, 트렌드 분석] 순서로 4개의 항목이 있어야 합니다.")

    problem_text, client_text, needs_text, trend_text = user_content

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
        model="ft:gpt-3.5-turbo-0125:personal::BWh2RT51", # ft:gpt-3.5-turbo-0125:personal::BWh2RT51 언어유희 ft:gpt-3.5-turbo-0125:personal::BXqc5T21 질문형형
        messages=messages,
        temperature=1.0,    # 기존 0.4
        max_tokens=1000
    )
    assistant_content = completion.choices[0].message["content"].strip()

    messages.append({"role": "assistant", "content": f"{assistant_content}"})

    print(f"\nGPT : {assistant_content}")
