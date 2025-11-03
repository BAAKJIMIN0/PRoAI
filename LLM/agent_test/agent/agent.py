import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import warnings
warnings.filterwarnings("ignore")   # Ignore all warnings
import logging
logging.basicConfig(level=logging.ERROR)
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import  LlmAgent #,LoopAgent, SequentialAgent, Agent
from typing import List, Dict
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from sub_agent import processor, pr_pipeline_agent, search_agent
from sub_agent.processor import processor
from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from google.adk.runners import InMemoryRunner
# from google.adk.tools.tool_context import ToolContext

load_dotenv()
if os.getenv("GOOGLE_API_KEY"):
    api_key = os.getenv("GOOGLE_API_KEY")
    
os.environ["GOOGLE_API_KEY"] = api_key

print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))

# class ConceptInput(BaseModel):
#     """광고/커뮤니케이션 콘셉트 도출에 필요한 입력 데이터 구조입니다."""
#     background: str = Field(description="문제 배경에 대한 상세 텍스트입니다.")
#     target: str = Field(description="주 타겟에 대한 상세 텍스트입니다.")
#     solution: str = Field(description="해결 과제에 대한 상세 텍스트입니다.")
#     content: str = Field(description="주요 내용에 대한 상세 텍스트입니다.")
#     assistance: str = Field(description="추가 분석 및 키워드에 대한 상세 텍스트입니다.")

# def execute_pipeline_fn(query: ConceptInput):
#     """
#     pr_pipeline_agent를 실행하고 결과를 반환하는 래퍼 함수입니다.
#     이 함수는 AgentTool 내부에서 사용되며, 입력은 Pydantic 모델로 변환됩니다.
#     """
#     return pr_pipeline_agent.run(ConceptInput) 

def get_rag(query: str, purpose: str)->List[Dict]:
    result = processor.query_vectordb(query, purpose=purpose, k=1)
    return result

root_agent = LlmAgent(
    name="prompt_agent",
    model="gemini-2.5-flash",      #config.root_agent_model,
    description=(
        "You are a root agent that helps users by using tools and agents through conversation."
    ),
    instruction=(
        """
        당신은 사용자 질문에 도구와 에이전트를 사용하여 답변하는 유능한 에이전트입니다.
        다음의 두가지 경우에 대해 각각 다른 워크플로우를 따르세요:
        
        1. 광고/커뮤니케이션 콘셉트 도출에 필요한 정보를 포함하는 경우:
        사용자의 입력에서 다음 5가지 정보(**문제 배경, 타겟, 해결 과제, 주요 내용, 추가 분석**)를 추출하세요.
        추출한 정보를 아래의 **Dictionary 형식**으로 구성한 후, 이 Dictionary를 **JSON 문자열로 변환**하세요.
        
        **Dictionary 형식 (JSON 문자열로 변환되어야 함):**
        {
            "background": 추출된 문제 배경 텍스트,
            "target": 추출된 주 타겟 텍스트,
            "solution": 추출된 해결 과제 텍스트,
            "content": 추출된 주요 내용 텍스트,
            "assistance": 추출된 추가 분석/키워드 텍스트
        }
        
        최종적으로 이 **JSON 문자열**을 `pr_pipeline_agent` 도구로 **호출(call)해야 합니다.** 

        
        2. 사용자의 질문에 단순 사실적 정보 검색이나 대답이 필요한 경우:
        사용자의 질문에 대해 적절한 도구(예: google_search)를 사용하여 필요한 정보를 검색하고, 그 정보를 바탕으로 답변을 생성하세요.
        """
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, # More deterministic output
        max_output_tokens=2000,
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            )
        ]
    ),
    include_contents='default',
    #output_key='query',
    tools=[AgentTool(agent=pr_pipeline_agent), AgentTool(agent=search_agent)]
)

APP_NAME = "Research agent"
USER_ID = "user_11"
SESSION_ID = "session_0011"
SESSION = None
RUNNER = None

async def call_agent_async(query: str, runner, user_id, session_id):
    """에이전트에게 쿼리를 보내고 최종 응답을 출력합니다."""
    print(f"\n>>> 사용자 쿼리: {query}")

    # 사용자의 쿼리를 Content 객체로 만듭니다.
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # 응답이 없을 경우 기본 응답 메시지
    final_response_text = "에이전트가 최종 응답을 생성하지 않았습니다."

    # run_async는 에이전트 로직을 실행하고 일련의 이벤트(Event)를 생성합니다.
    # 이벤트를 순회하며 최종 응답을 찾게 됩니다.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):

        # Event에서 어떤 작업이 일어나는지 확인
        print(f"  [Event] author: {event.author}, Type: {type(event).__name__}, Response: {event.is_final_response()}, Content: {event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                # 첫 번째 파트(part)에 텍스트 응답이 있다고 가정합니다.
                final_response_text = event.content.parts[0].text


            elif event.actions and event.actions.escalate: # 에이전트가 작업을 수행하다가 해결할 수 없는 경우입니다.
                final_response_text = f"Agent 오류 발생: {event.error_message or '특정 메시지 없음.'}"


            # 최종 응답을 찾으면 이벤트 처리를 중단합니다.
            break

    print(f"<<< 에이전트 응답: {final_response_text}")
    
async def setup_and_run(query: str, root_agent, APP_NAME, USER_ID, SESSION_ID):
    """세션을 설정하고 에이전트를 실행하는 비동기 함수"""
    
    session_service = InMemorySessionService()
    
    SESSION = await session_service.create_session( 
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    RUNNER = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{RUNNER.agent.name}'.")
    
    # 세션과 러너를 설정한 후 대화를 실행
    await call_agent_async(query, 
        runner=RUNNER, 
        user_id=USER_ID, 
        session_id=SESSION_ID)
    
async def run_conversation(query):
    await call_agent_async(query,
        runner=RUNNER,
        user_id=USER_ID,
        session_id=SESSION_ID)

if __name__ == "__main__":
    asyncio.run(setup_and_run(
        query='''
            'background': '지역 특산물은 품질이 좋아도 MZ세대 인지도가 낮음'
            'solution': '전통적인 이미지를 현대적으로 재해석'
            'target': '20~30대 로컬 소비 관심층, 여행을 즐기는 젊은 세대'
            'content': '지역의 가치를 힙하고 재미있게 소비할 수 있다는 메시지'
            'assistance': '로컬푸드, 힙한전통, 맛있는여행'
        ''',
        root_agent=root_agent, 
        APP_NAME=APP_NAME, 
        USER_ID=USER_ID, 
        SESSION_ID=SESSION_ID
    ))
