from app.agents.base import BaseAgent
from app.agents.logistics_agent import logistics_agent
from app.agents.health_agent import health_agent
from app.agents.infrastructure_agent import infrastructure_agent
from app.agents.evacuation_agent import evacuation_agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
import asyncio
from google.genai import types as genai_types

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CoordinatorAgent",
            instruction="This agent is responsible for coordinating the other agents and providing a consolidated response.",
            tools=[],
        )

    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        hazard_info = context.session.state.get("hazard_info")
        self.log(f"Coordinating response for hazard: {hazard_info}")
        hazard_type = hazard_info.get("hazard")

        tasks = []
        if hazard_type.lower() == "flood":
            tasks.append(logistics_agent.handle_hazard(hazard_info))
            tasks.append(health_agent.handle_hazard(hazard_info))
            tasks.append(evacuation_agent.handle_hazard(hazard_info))
        elif hazard_type.lower() == "earthquake":
            tasks.append(logistics_agent.handle_hazard(hazard_info))
            tasks.append(health_agent.handle_hazard(hazard_info))
        elif hazard_type.lower() == "storm":
            tasks.append(logistics_agent.handle_hazard(hazard_info))
            tasks.append(evacuation_agent.handle_hazard(hazard_info))

        # Run tasks in parallel
        responses = await asyncio.gather(*tasks)

        # Consolidate responses
        consolidated_report = f"""
        Hazard Detected: {hazard_info.get('hazard')} at {hazard_info.get('location')} with intensity {hazard_info.get('intensity')}.
        """
        
        for response in responses:
            consolidated_report += f"\n{response}\n"

        self.log(f"Consolidated report: {consolidated_report}")
        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=consolidated_report)]))

coordinator_agent = CoordinatorAgent()
