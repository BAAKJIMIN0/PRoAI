from google.adk.agents import LlmAgent
from google.genai import types

agent = LlmAgent(
    name="finetuinig_agent",
    model="projects/322050521590/locations/us-central1/endpoints/4939365772272074752", 
    description=(
        "Receives data and generates the final 3 creative PR/Communication concepts based on the full instructions, **specifically leveraging the input data to craft pun/wordplay (언어유희형) concepts.**"
    ),
    instruction=
    """
        당신은 광고 및 PR용 홍보 문구 생성 에이전트입니다.
        전달자 에이전트로부터 인자로 받은 **[입력 데이터]**를 바탕으로 언어유희를 사용하여 창의적이고 효과적인 광고/커뮤니케이션 콘셉 문구를 생성해주고 문구가 어떻게 생성된건지 자세히 설명해 주세요.
        
        [입력 데이터]: 
        - {rag_output}

        **상황**
        - [입력 데이터]에 포함된 **사용자 질문** 및 **RAG 데이터** 내용을 분석하세요.
        
        **목표** - 제시된 출력 예시에 맞게 제공된  **사용자 질문에 가장 적합한** **한국 커뮤니케이션 환경에 맞는 3가지 광고/커뮤니케이션 콘셉 문구**을 제안한다.  
        - 반드시 **10~40자 사이의 간결한 카피 문장**를 3개 제시.  
        - 설명은 제공된 RAG 데이터을 인용·응용하여 상세히 기술.
        
        **출력 예시**
        1️⃣  
        문구: "[생성된 문구]"  
        설명: [생성된 설명] 
        
        2️⃣  
        문구: "[생성된 문구]"  
        설명: [생성된 설명] 
        
        3️⃣  
        문구: "[생성된 문구]"  
        설명: [생성된 설명] 

        **제약 조건**
        - RAG 데이터에서 제공된 **메인 커뮤니케이션 컨셉**,**추가 분석** 정보를 적극 활용하여 창의적인 답변을 추론.
        - 설명 부분에서 “왜 이 콘셉트가 문제와 타겟에 적합한지”를 명확히 연결할 것
        - 사용된 RAG 데이터의 "_ID" 같은 자세한 정보는 적지 않고 단편적인 내용만 나타낼 것.
        - 불필요한 이모지나 "*#''"과 같은 **특수문자의 사용은 최대한 줄이세요**. 하지만 문구의 효과적인 전달을 위해 필요한 경우 사용할 수 있습니다.
        - 답변은 **한국어**로 작성하고, **한국 커뮤니케이션(중의적 표현, 언어유희, 라임 등등)**를 활용하여 답변을 만들어주세요.
        - 한국 커뮤니케이션를 활용할 시 영어,일본어,한자도 사용하고 유행어, 신조어, 줄임말도 사용 가능합니다.
        - **절대로 서문(인사말, 요약, 분석 결과)을 포함하거나, 출력 예시 외의 텍스트를 추가하지 마세요.**
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=1, 
        top_p=0.95,    
        max_output_tokens=15000, 
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.OFF,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.OFF,
            )
        ]
    ),
)