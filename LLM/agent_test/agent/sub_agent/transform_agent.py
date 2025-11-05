from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
#from ..config import config
#from typing import Dict, List
from google.genai import types
from .finetuning_agent import wordplay_agent, question_agent

agent = Agent(
    name="TransfromAgent",
    model="gemini-2.5-flash",
    description=("Analyzes the expression type and dispatches the RAG data to the specialized concept generation agent (bagent)."),
    instruction=
    """
        당신은 광고/PR 콘셉트 워크플로우를 관리하는 전달자 에이전트입니다.
        
        **[가장 중요한 제약]:**
        1. **무조건** 도구를 호출해야 합니다.
        2. 도구 호출이 **실패**했을 경우, **"ERROR: 도구 호출에 실패하여 문구 생성을 완료하지 못했습니다. 반드시 도구를 호출해야 합니다."** 라는 문자열을 **그대로** 출력해야 합니다.
        3. 문구 생성은 **절대로 직접 수행해서는 안 됩니다**. 문구 생성은 오직의 호출한 도구의 출력만을 사용해야 합니다.

        [입력 데이터]: 
        - {rag_output}

        **[워크플로우]**
        1. **표현 유형 분석:** [입력 데이터]에 포함된 "표현 유형" 정보를 추출하여 분석합니다.
        2. **도구 호출:** **반드시** 도구를 호출하세요.
        3. **최종 출력:** 도구의 실행 결과(최종 문구 3가지)를 **수정 없이 그대로** 최종 출력으로 반환합니다.

        **[추가 제약 조건]**
        - 절대로 서문(인사말, 요약, 분석 결과)을 포함하거나, 출력 예시 외의 텍스트를 추가하지 마세요.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, # 도구 호출의 안정성을 위해 낮은 Temperature 권장
        top_p=0.95, max_output_tokens=15000,
    ),
    output_key="transform_output",
    tools=[AgentTool(agent=wordplay_agent.agent),AgentTool(agent=question_agent.agent)] 
)