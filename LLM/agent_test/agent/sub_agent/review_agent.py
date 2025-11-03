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

        [생성된 답변]:
        - {transform_output}

        evaluation 결과 기반 [개선 사항]:
        {evaluation_output}

        
        **다음 사항을 고려해주세요:**
        - [생성된 답변]의 출력 형태를 최대한 유지하세요.
        - **전달된 평가 결과([개선 사항])를 반영하여 품질 향상**
        - 이 데이터를 바탕으로 광고 및 마케팅 전략에 활용할 수 있는 정제된 콘텐츠를 한국어로 생성해주세요. 
        - 불필요한 이모지나 "*#''"과 같은 **특수문자의 사용은 최대한 줄이세요**. 하지만 문구의 효과적인 전달을 위해 필요한 경우 사용할 수 있습니다.
        - 차별화된 인사이트 강조
        - 실전 마케팅에 바로 활용 가능한 형태

        인사이트를 종합하여 필요시 생성된 답변을 개선(refactoring)해주고 문제가 없다면 그대로 전달해주세요.
        """,
    output_key="final_answer"
)