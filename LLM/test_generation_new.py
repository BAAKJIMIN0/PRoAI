import os,sys
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from dotenv import load_dotenv
import openai 
from langchain.schema import Document
#from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.")
openai.api_key = OPENAI_API_KEY
#openai = OpenAI(api_key=OPENAI_API_KEY)

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/test')
#CHROMA_COLLECTION_NAME = "RAG_test"

embedding_model = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask"
)

def create_prompt(query: dict):
    # 각 질문과 가장 관련있는 본문 3개를 가져옴
    problem = query_vectordb(query["background"], use_retriever=True, purpose="background")
    client = query_vectordb(query["target"], use_retriever=True, purpose="target")
    needs = query_vectordb(query["solution"], use_retriever=True, purpose="solution")
    information = query_vectordb(query["content"], use_retriever=True, purpose="content")
    keyword = query_vectordb(query["assistance"], use_retriever=True, purpose="assistance")
    
    result = problem + client + needs + information + keyword

    # 결과 출력
    print('----------------------------------------------------------')
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
        당신은 광고 및 커뮤니케이션 전략에 정통한 전문가입니다.

        참조된 'docs_test' 는 문제 정의, 타겟, 솔루션, 핵심 키워드를를 기반으로 검색된 문서들입니다.
        참조된 문서의 '메인 커뮤니케이션 컨셉' 부분을 인용하여 창의적인 답변을 추론해주세요.
        명시적인 내용이 없을 경우 문맥 기반의 논리적 추론을 통해 사용자 질문에 답변해 주세요.
        답변은 한국어로 작성하되, 언어유희 경우 영어도 활용해 주세요.

        --- 사용자 질문 ---
        \"\"\"{str(query)}\"\"\"

        --- 요구사항 ---
        background에 해당되는 문제점을 파악하고, target 연령대에 맞는 컨셉으로, solution에 해당되는 내용에 맞게,
        assistance의 내용을 참고하여, 다음 기준에 따라 **3가지 커뮤니케이션 콘셉트 스타일**을 제안하세요:

        1. 다양한 스타일의 유형(문제해결형, 트렌드반영형, 참여유도형, 감성추구형, 관심주목형) 중 **문제에 가장 적합한 3가지**를 선정하세요.(!중요! 다른 유형 사용금지)
        2. 각 스타일은 서로 명확히 다른 접근을 취해야 하며, **GPT가 문맥상 가장 효과적인 조합**을 판단하여 선택해야 합니다.
        3. 각 콘셉트는 다음의 3가지 요소를 포함해야 합니다:
            - ✅ 콘셉트 유형명 (1. 문제해결형, 2. 트렌드반영형, 3. 참여유도형, 4 . 감성추구형, 5. 관심주목형 중 하나)
            - ✅ 해당 스타일로 작성한 콘셉트 문구 (반드시 10~40자 사이의 간결한 문장으로 작성)
            - ✅ 이유 또는 목적을 가능하면 참조된 docs_test의 추가 분석을 활용해 자세하게 설명 (이 스타일이 문제 정의와 타겟에 어떻게 부합하며, 어떤 메시지를 전달하고자 하는지 설명해 주세요.)
        4. 답변을 한국 커뮤니케이션 환경에 맞게 언어유희, 신조어, 속어 , 한자나 영어를 활용한 중의적 표현 등을 활용해 창의적으로 작성하세요.

        예시 형식:
        1️⃣ [유형명]  
        문구: "..."  
        설명: ...   (설명은 도출된 컨셉을 구체적으로 작성)

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

    # vecotordb 로드
    vectordb_A = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model,
        collection_name="RAG_A",
    )
    
    vectordb_B = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model,
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
        #all_docs = vectordb_A.similarity_search(query, k=5)  # 충분히 가져오기
        all_docs = vectordb_A._collection.get(
            where={"idx": {"$in": idx_list}},   # metadata 필터
            include=["metadatas", "documents"]
        )
        
        top_docs = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(all_docs["documents"], all_docs["metadatas"])
        ]
        
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
        problem = input("문제 정의: ").strip()
        user_content.append(problem.strip())

        client = input("타겟 설정: ").strip()
        user_content.append(client.strip())

        needs = input("해결 과제: ").strip()
        user_content.append(needs.strip())
        
        information = input("전달 정보: ").strip()
        user_content.append(information.strip())

        keyword = input("핵심 키워드: ").strip()
        user_content.append(keyword.strip())
    except (KeyboardInterrupt, EOFError):
        print("\n입력 종료")
        break

    if not user_content:
        print("입력 내용이 없습니다. 다시 입력해 주세요.")
        continue
    
    print("\n입력 내용" + f"\n{user_content}\n")
    
    # user_content는 문제정의, 타겟설정, 해결과제, 전달정보, 트렌드 분석 순
    if len(user_content) != 5:
        raise ValueError("user_content는 [문제정의, 타겟설정, 해결과제, 전달정보, 트렌드 분석] 순서로 5개의 항목이 있어야 합니다.")

    problem_text, client_text, needs_text, information_text, keyword_text = user_content

    messages = create_prompt(
        {
            "background": problem_text,
            "target": client_text,
            "solution": needs_text,
            "content": information_text,
            "assistance": keyword_text
        }
    )

    # GPT 출력
    completion = openai.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal::BWh2RT51", # ft:gpt-3.5-turbo-0125:personal::BWh2RT51 언어유희 ft:gpt-3.5-turbo-0125:personal::BXqc5T21 질문형 ft:gpt-3.5-turbo-0125:personal::BhBKYQy5 둘다다
        messages=messages,
        temperature=1.0,    # 기존 0.4
        max_tokens=500  # gpt 버전 5 이상은 max_completion_tokens
    )
    
    assistant_content = completion.choices[0].message.content.strip()

    messages.append({"role": "assistant", "content": f"{assistant_content}"})

    print(f"\nGPT : {assistant_content}")
