from app.agents.base import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
import asyncio
from google.genai import types as genai_types

class CoordinatorAgent(BaseAgent):
    def __init__(self, logistics_agent, health_agent, evacuation_agent, infrastructure_agent):
        super().__init__(
            name="CoordinatorAgent",
            instruction="This agent is responsible for coordinating the other agents and providing a consolidated response.",
            tools=[],
        )
        self.logistics_agent = logistics_agent
        self.health_agent = health_agent
        self.evacuation_agent = evacuation_agent
        self.infrastructure_agent = infrastructure_agent

    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        hazard_info = context.session.state.get("hazard_info")

        if hazard_info is None:
            self.log("Could not retrieve hazard information from state.", severity="ERROR")
            yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="No hazard information available to coordinate.")]))
            return
            
        self.log(f"Coordinating response for hazard", hazard_info=hazard_info)
        hazard_type = hazard_info.get("hazard")

        tasks = []
        if hazard_type.lower() == "flood":
            self.log("Adding logistics, health, and evacuation agents to tasks.")
            tasks.append(self.logistics_agent.handle_hazard(hazard_info))
            tasks.append(self.health_agent.handle_hazard(hazard_info))
            tasks.append(self.evacuation_agent.handle_hazard(hazard_info))
        elif hazard_type.lower() == "earthquake":
            self.log("Adding logistics and health agents to tasks.")
            tasks.append(self.logistics_agent.handle_hazard(hazard_info))
            tasks.append(self.health_agent.handle_hazard(hazard_info))
        elif hazard_type.lower() == "storm":
            self.log("Adding logistics and evacuation agents to tasks.")
            tasks.append(self.logistics_agent.handle_hazard(hazard_info))
            tasks.append(self.evacuation_agent.handle_hazard(hazard_info))

        # Run tasks in parallel
        self.log(f"Running {len(tasks)} tasks in parallel.")
        responses = await asyncio.gather(*tasks)

        # Consolidate responses
        consolidated_report = f"""
        Hazard Detected: {hazard_info.get('hazard')} at {hazard_info.get('location')} with intensity {hazard_info.get('intensity')}.
        """
        
        for response in responses:
            consolidated_report += f"\n{response}\n"

        self.log(f"Consolidated report generated.", consolidated_report=consolidated_report)
        yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text=consolidated_report)]))


