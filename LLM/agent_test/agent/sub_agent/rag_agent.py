from google.adk.agents import Agent
from sub_agent.processor import processor
from typing import List, Dict


def get_rag(query: str, purpose: str)->List[Dict]:
    result = processor.query_vectordb(query, purpose=purpose, k=1)
    return result

agent = Agent(
    name="prompt_agent",
    model="gemini-2.5-flash",      #config.root_agent_model,
    description=(
        "You are a root agent that helps users by using tools and agents through conversation."
    ),
    instruction=(
        """
        당신은 사용자 질문에 도구와 에이전트를 사용하여 답변하는 유능한 에이전트입니다.
        다음 워크플로우를 따르세요:

        # RAG 데이터 획득:
        - 제공된 사용자 질문 각 항목(background, target, solution, content, assistance)을 기반으로, 'purpose'는 항목의 'key'로, 'query'는 항목의 'value'로 하여 get_rag 도구를 순차적으로 호출하세요.
        - 예시 호출:
        - background 데이터를 위해: get_rag(query={request['background']}, purpose='background')
        - target 데이터를 위해: get_rag(query={request['target']}, purpose='target')
        - ... 이와 같이 나머지 항목들도 반복합니다.
        - 모든 호출의 결과 **그대로**를 종합하여 Dictionary 형식으로 통합하세요.

        **Dictionary 형식:**
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

        최종적으로 가져온 데이터 결과를 전달해주세요.
        """
    ),
    output_key='rag_output',
    tools=[get_rag]
)