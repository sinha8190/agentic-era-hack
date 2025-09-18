from google.adk.agents import SequentialAgent
from app.agents.hazard_agent import HazardAgent
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.logistics_agent import LogisticsAgent
from app.agents.health_agent import HealthAgent
from app.agents.evacuation_agent import EvacuationAgent
from app.agents.infrastructure_agent import InfrastructureAgent
from app.utils.tracing import CloudTraceLoggingSpanExporter

# Instantiate the logger
exporter = CloudTraceLoggingSpanExporter()

# Instantiate agents
logistics_agent = LogisticsAgent()
health_agent = HealthAgent()
evacuation_agent = EvacuationAgent()
infrastructure_agent = InfrastructureAgent()
hazard_agent = HazardAgent()
coordinator_agent = CoordinatorAgent(
    logistics_agent=logistics_agent,
    health_agent=health_agent,
    evacuation_agent=evacuation_agent,
    infrastructure_agent=infrastructure_agent,
)

root_agent = SequentialAgent(
    name="CrisisIQ",
    sub_agents=[
        hazard_agent,
        coordinator_agent,
    ],
)
