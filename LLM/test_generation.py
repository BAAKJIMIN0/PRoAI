
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

    # user_content = f"""
    #     당신은 광고 및 마케팅 전략 전문가입니다.

    #     다음은 문제정의, 타겟, 솔루션, 트렌드 분석을 바탕으로 추출된 관련 문서들입니다.
    #     이 문서를 기반으로 아래 질문에 대해 다음과 같은 방식으로 응답해 주세요:

    #     1. 문서 내용을 적극적으로 인용하여 질문에 답변합니다.
    #     2. 문서에 명확한 내용이 없다면, 그 사실을 명확히 밝히고 상식적 기반으로 보완 설명합니다.
    #     3. 응답은 반드시 한국어로 작성합니다.
    #     4. 마지막에 '커뮤니케이션 콘셉트 문구'를 생성합니다. (문서 기반)
    #     5. 총 3가지 형식으로 각각 다른 스타일로 변형하여 제시하세요.
    #     - ✅ **형식 1**: 핵심 요약형 슬로건 (10자 내외)
    #     - ✅ **형식 2**: 광고 카피형 (1~2문장, 감성 강조)
    #     - ✅ **형식 3**: 전략적 설명형 (2~4문장, 논리 기반)

    #     💡 사용자 질문:
    #     \"\"\"{query}\"\"\"
    #     """
    
    # user_content = f"""
    #     User question: "{str(query)}". 
    #     Answer the question based on the DB-RAG documents above.
    #     If it is in the document, actively refer to the document and create an answer. 
    #     If it is not in the document, inform the user that it is not in the document and create an appropriate answer.
    #     Finally, refer to the document to create the most appropriate Comunication concept phrase.
    #     Answer in Korean.
    #     Give at least three different variations concepts of the answer in different formats.
    # """

    # user_content = f"""
    # User question: "{str(query)}". 
    # Please answer based on the DB-RAG documents provided above.

    # If the document clearly includes relevant content, use it in your answer.  
    # If not, infer a possible answer by combining related insights or trends from the documents.  

    # Respond in Korean. At the end, generate 3 creative variations of a communication concept based on the content.
    # """
    print("질문문자열:",str(query))
    user_content = f"""
        당신은 광고 및 커뮤니케이션 전략에 정통한 전문가입니다.

        아래는 문제 정의, 타겟, 솔루션, 트렌드 분석을 기반으로 검색된 문서들입니다.
        이 문서를 적극적으로 인용하거나, 명시적인 내용이 없을 경우 문맥 기반의 논리적 추론을 통해 사용자 질문에 답변해 주세요.
        답변은 한국어로 작성하되, 언어유희 경우 영어도 활용해 주세요.

        --- 사용자 질문 ---
        \"\"\"{str(query)}\"\"\"

        --- 요구사항 ---
        background에 해당되는 문제점을 파악하고, target 연령대에 맞는 컨셉으로, solution에 해당되는 내용에 맞게,
        assistance의 내용을 참고하여, 다음 기준에 따라 **3가지 커뮤니케이션 콘셉트 스타일**을 제안하세요:

        1. 다양한 스타일(문제해결형, 트렌드반영형, 참여유도형, 감성추구형, 관심주목형) 중 **문제에 가장 적합한 3가지**를 선정하세요.
        2. 각 스타일은 서로 명확히 다른 접근을 취해야 하며, **GPT가 문맥상 가장 효과적인 조합**을 판단하여 선택해야 합니다.
        3. 각 콘셉트는 다음의 3가지 요소를 포함해야 합니다:
            - ✅ 콘셉트 유형명 (자유롭게 정하되 명확할 것)
            - ✅ 해당 스타일로 작성한 콘셉트 문구 (반드시 10~40자 사이의 간결한 문장으로 작성)
            - ✅ 간단한 이유 또는 목적 설명 (이 스타일이 문제 정의와 타겟에 어떻게 부합하며, 어떤 메시지를 전달하고자 하는지 간결히 설명해 주세요.)

        예시 형식:
        1️⃣ [유형명]  
        문구: "..."  
        설명: ...

        ---
        응답 형식은 위 예시와 유사하게, 콘셉트 3가지를 우선순위 순으로 제시하세요.
        """



    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_content},
    ]
    return messages

def query_vectordb(query: str, purpose: str, use_retriever: bool = False):
    from pprint import pprint

    # 벡터DB 단일화
    vectordb = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name="RAG_B",  # 기존 A로 통일
    )
    docs = vectordb.similarity_search("대학생", k=1)
    print(docs[0].metadata)
    if use_retriever:
        print("\n[retriever 사용] section 필터:", purpose)

        # section 필터 기반으로 관련 문서 검색
        retriever = vectordb.as_retriever(
            search_kwargs={"k": 3},
            filter={"section": purpose}
        )
        top_docs = retriever.get_relevant_documents(query)

    else:
        print("\n[similarity_search 사용]")

        # 단순 벡터 유사도 기반 검색
        top_docs = vectordb.similarity_search(query, k=3)

    pprint(top_docs)
    return top_docs


messages = []
user_content = []

while True:
    try: 
        problem = input("문제 정의: ").strip()
        user_content.append(problem.strip())

        client = input("타겟 설정: ").strip()
        user_content.append(client.strip())

        needs = input("니즈 파악: ").strip()
        user_content.append(needs.strip())

        trend = input("트렌드 분석: ").strip()
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
