from google.adk.agents import SequentialAgent
from app.agents.hazard_agent import hazard_agent
from app.agents.coordinator_agent import coordinator_agent

root_agent = SequentialAgent(
    name="CrisisIQ",
    sub_agents=[
        hazard_agent,
        coordinator_agent,
    ],
)
