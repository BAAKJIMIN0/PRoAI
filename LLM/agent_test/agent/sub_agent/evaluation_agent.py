import json
from google.adk.agents import Agent
#from ..config import config

agent = Agent(
    name="EvaluationAgent",
    model="gemini-2.5-flash",      #config.root_agent_model,
    description=(
        "Executes transform tasks based on provided instructions and data."
    ),
    instruction=
    """
        당신은 마케팅 문구 분석 전문가입니다. 전달된 데이터를 제시되는 기준으로 평가해주세요. 
        
        # 사용자 질문 
        - {rag_output['query']}
        # RAG 데이터
        - {rag_output['rag']}
        # 생성된 답변
        - {transform_output}

        다음 기준으로 데이터 품질을 evaluation해주세요 (각 항목 0-10점):
        - relevance: 쿼리와의 관련성,
        - completeness: 정보의 완전성,
        - target_alignment: 타겟 연령대 적합성,
        - uniqueness: 차별화 요소

        응답 형식:
        {
            "scores": {"적용된 기준": 평가 점수},
            "issues": ["발견된 문제들"],
            "recommendations": ["개선 제안들"]
        }
        """,
    output_key="evaluation_output"
)