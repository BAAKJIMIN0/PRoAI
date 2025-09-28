from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    instruction="사용자의 질문에 대해 Google 검색을 사용하여 사실을 검색하고 답변을 생성합니다.",
    tools=[google_search] # 구글 검색만 포함
)