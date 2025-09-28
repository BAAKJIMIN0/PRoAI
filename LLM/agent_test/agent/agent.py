from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
from google import genai
from google.adk.agents import LoopAgent, LlmAgent, SequentialAgent, Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.tool_context import ToolContext
#from google.adk.events import EventActions
from typing import Dict
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from pydantic import BaseModel, Field
from sub_agent import pr_pipeline_agent
#from .config import config
import os
from dotenv import load_dotenv

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# thinking_config = ThinkingConfig(
#     include_thoughts=True,   # Ask the model to include its thoughts in the response
#     thinking_budget=256      # Limit the 'thinking' to 256 tokens (adjust as needed)
# )
# print("ThinkingConfig:", thinking_config)

# # Step 2: Instantiate BuiltInPlanner
# planner = BuiltInPlanner(
#     thinking_config=thinking_config
# )

load_dotenv()
if os.getenv("GOOGLE_API_KEY"):
    api_key = os.getenv("GOOGLE_API_KEY")
    
os.environ["GOOGLE_API_KEY"] = api_key
os.environ["GENAI_API_KEY"] = api_key 

print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))

class ConceptInput(BaseModel):
    """광고/커뮤니케이션 콘셉트 도출에 필요한 입력 데이터 구조입니다."""
    background: str = Field(description="문제 배경에 대한 상세 텍스트입니다.")
    target: str = Field(description="주 타겟에 대한 상세 텍스트입니다.")
    solution: str = Field(description="해결 과제에 대한 상세 텍스트입니다.")
    content: str = Field(description="주요 내용에 대한 상세 텍스트입니다.")
    assistance: str = Field(description="추가 분석 및 키워드에 대한 상세 텍스트입니다.")


def execute_pipeline(query: ConceptInput):
    """
    pr_pipeline_agent를 실행하고 결과를 반환하는 래퍼 함수입니다.
    이 함수는 AgentTool 내부에서 사용되며, 입력은 Pydantic 모델로 변환됩니다.
    """
    return pr_pipeline_agent.run(ConceptInput) 


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
        1. 사용자의 입력(query)이 광고/커뮤니케이션 콘셉트 도출에 필요한 정보(문제 배경, 타겟, 해결 과제, 주요 내용, 추가 분석)를 포함하고 있지 않은 경우:
        사용자의 입력(query)이 광고/커뮤니케이션 콘셉트 도출에 필요한 **문제 배경(background), 타겟(target), 해결 과제(solution), 주요 내용(content), 추가 분석(assistance) 등의 정보**를 포함하고 있다면, 
        이 정보들을 추출하여 아래의 **정의된 dictionary 형식**으로 재구성한 후, 
        **반드시** `execute_pipeline` 도구를 사용하여 이 dictionary를 전달해야 합니다.

        **Dictionary 형식:**
        {"rag" : Tool(execute_pipeline)로 가져온 데이터 결과,
        "query":
            {
                "background": 사용자 입력에서 추출된 문제 배경 텍스트,
                "target": 사용자 입력에서 추출된 주 타겟 텍스트,
                "solution": 사용자 입력에서 추출된 해결 과제 텍스트,
                "content": 사용자 입력에서 추출된 주요 내용 텍스트,
                "assistance": 사용자 입력에서 추출된 추가 분석/키워드 텍스트
            }
        }
        최종적으로 `execute_pipeline`가 생성한 결과물을 사용자에게 전달하세요.
        """
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, # More deterministic output
        max_output_tokens=250,
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            )
        ]
    ),
    # planner=planner, # Assign the planner to the agent
    include_contents='default',
    output_key='data',
    tools=[execute_pipeline,]
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
        'background': '자격증·취미교육 시장 포화, 기존 광고 방식은 정보 중심으로 차별성 부족'
        'solution': '‘변화’와 ‘성과’ 중심으로 메시지 재구성, 광고 클릭 시 명확한 이점 제공'
        'target': '20~40대 직장인 및 취업 준비생, 실질적인 결과에 민감한 교육 소비자'
        'content': '무료 교재, 합격 후기 강조, 인플루언서 모델 등장 광고, 동영상·네이티브 이미지 광고 활용'
        'assistance': '기대효과, 무료혜택, 후기, 인플루언서, 네이티브광 고, “이거 하면 나도 달라질 수 있겠다”, “유명인이 추천하네”, “무료니까 한 번 해볼까?”'
        ''',
        root_agent=root_agent, 
        APP_NAME=APP_NAME, 
        USER_ID=USER_ID, 
        SESSION_ID=SESSION_ID
    ))
