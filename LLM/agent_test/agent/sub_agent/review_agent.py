from google.adk.agents import Agent
#from ..config import config

agent = Agent(
    name="ReviewAgent",
    model="gemini-2.5-flash",      #config.root_agent_model,
    description=(
        "Executes transform tasks based on provided instructions and data."
    ),
    instruction=
    """
        다음은 전달된 데이터입니다:
        # 사용자 질문 
        - {rag_output['query']}
        # RAG 데이터
        - {rag_output['rag']}
        # 생성된 답변
        - {transform_output}

        evaluation 결과 기반 개선 사항:
        {evaluation_output}

        이 데이터를 바탕으로 광고 및 마케팅 전략에 활용할 수 있는 정제된 콘텐츠를 한국어로 생성해주세요. 
        다음 사항을 고려해주세요:

        1. 각 카테고리의 핵심 메시지를 명확히 전달
        2. 타겟 연령대에 맞는 어조와 한국형 커뮤니케이션 표현 사용
        3. 문제 해결 중심의 접근
        4. 차별화된 인사이트 강조
        5. 실전 마케팅에 바로 활용 가능한 형태

        인사이트를 종합하여 필요시 결과를 개선(refactoring)해주고 문제가 없다면 그대로 전달해주세요.
        """,
    output_key="final_answer"
)