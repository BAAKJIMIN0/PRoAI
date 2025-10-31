from google.adk.agents import SequentialAgent
from . import transform_agent,rag_agent, evaluation_agent, review_agent, test_agent
# from ..config import config

pr_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    description=(
        "Executes a sequence of tasks."
    ),
    sub_agents=[rag_agent.agent, transform_agent.agent, evaluation_agent.agent, review_agent.agent]    #test_agent.agent, transform_agent.agent, evaluation_agent.agent, review_agent.agent],
)

#"Executes a sequence of **advertising/communication concept transformation**, evaluation, and review tasks."