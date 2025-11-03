from google import genai
from google.genai import types
import base64
import os
from dotenv import load_dotenv

load_dotenv()
if os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    
prompt_text = '''
    'background': '지역 특산물은 품질이 좋아도 MZ세대 인지도가 낮음'
    'solution': '전통적인 이미지를 현대적으로 재해석'
    'target': '20~30대 로컬 소비 관심층, 여행을 즐기는 젊은 세대'
    'content': '지역의 가치를 힙하고 재미있게 소비할 수 있다는 메시지'
    'assistance': '로컬푸드, 힙한전통, 맛있는여행'
'''
    
def generate():
  client = genai.Client(
        vertexai=True, project='gen-lang-client-0616751325', location='us-central1'
    )


  model = "projects/322050521590/locations/us-central1/endpoints/3372007548830875648"
  contents = [
    types.Content(
      role="user",
      parts=[
        types.Part(text=prompt_text)
      ]
    )
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 65535,
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    thinking_config=types.ThinkingConfig(
      thinking_budget=0,
    ),
  )

  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    print(chunk.text, end="")

generate()