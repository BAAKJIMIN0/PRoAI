from google.adk.agents import Agent
from sub_agent.processor import processor
from typing import List, Dict


def get_rag(query: str, purpose: str):  #->List[Dict]
    """
    query: 검색할 문장 (예: 'MZ세대 인지도 낮음')
    purpose: 검색 목적 (예: 'background', 'target', 'solution', ...)
    """
    result = processor.query_vectordb(query, purpose=purpose, k=1)
    return result

agent = Agent(
    name="rag_agent",
    model="gemini-2.5-flash",      #config.root_agent_model,
    description=(
        "You are a root agent that helps users by using tools and agents through conversation."
    ),
    instruction=(
        """
        당신은 사용자 질문에 맞는 문서를 찾아 RAG를 하는 에이전트입니다.
        다음 워크플로우를 따르세요:

        1. RAG 데이터 획득:
        - **[입력 데이터]** (JSON 문자열)를 **파싱**하여 5가지 항목(background, target, solution, content, assistance)을 추출하세요.
        - 추출된 각 항목을 기반으로, 'purpose'는 항목의 'key'로, 'query'는 항목의 'value'로 하여 get_rag 도구를 순차적으로 호출하세요.
        - 모든 호출의 결과 **그대로**를 종합하여 LLM에게 전달해 주세요.
        
        2. 최종적으로 아래의 **텍스트 보고서 형식**으로 정보를 요약하여 다음 agent에게 전달해주세요.
        
        **텍스트 보고서 형식:**
        
        표현 유형:
            "입력 데이터에서 추출된 표현 유형(예: 언어유희형, 질문형, 정보전달형)"
        
        사용자 질문:
            "background": 사용자 입력에서 추출된 문제 배경 텍스트,
            "target": 사용자 입력에서 추출된 주 타겟 텍스트,
            "solution": 사용자 입력에서 추출된 해결 과제 텍스트,
            "content": 사용자 입력에서 추출된 주요 내용 텍스트,
            "assistance": 사용자 입력에서 추출된 추가 분석/키워드 텍스트
            
        RAG 데이터:
            [background에 대해 Tool(get_rag)로 가져온 데이터 결과]
            [target에 대해 Tool(get_rag)로 가져온 데이터 결과]
            [solution에 대해 Tool(get_rag)로 가져온 데이터 결과]
            [content에 대해 Tool(get_rag)로 가져온 데이터 결과]
            [assistance에 대해 Tool(get_rag)로 가져온 데이터 결과]
        """
    ),
    output_key='rag_output',
    tools=[get_rag]
)

'''
{"rag" : Tool(get_rag)로 가져온 데이터 결과,
        "query":
            {
                "background": 사용자 입력에서 추출된 문제 배경 텍스트,
                "target": 사용자 입력에서 추출된 주 타겟 텍스트,
                "solution": 사용자 입력에서 추출된 해결 과제 텍스트,
                "content": 사용자 입력에서 추출된 주요 내용 텍스트,
                "assistance": 사용자 입력에서 추출된 추가 분석/키워드 텍스트
            }
        }
'''