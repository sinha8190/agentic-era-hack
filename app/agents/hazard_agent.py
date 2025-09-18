from google.adk.agents import LoopAgent
from app.agents.base import BaseAgent
import json
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
import asyncio
from google.genai import types as genai_types

class HazardReaderAgent(BaseAgent):
    """An agent that reads hazard status from a file and saves it to the session state."""
    def __init__(self, name: str):
        super().__init__(name=name, instruction="", tools=[])

    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        try:
            with open("app/data/hazard_status.json") as f:
                hazard_data = json.load(f)
            self.log("Read hazard data from file", hazard_data=hazard_data)
            
            # Get the first hazard from the list
            first_hazard = hazard_data.get("hazards", [])[0]

            # The coordinator agent expects "hazard" and "intensity" keys, 
            # but the new structure has "type" and "severity". I will map them.
            flattened_hazard_info = {
                "hazard": first_hazard.get("type"),
                "location": first_hazard.get("location"),
                "intensity": first_hazard.get("severity"),
                "description": first_hazard.get("description"),
                "timestamp": first_hazard.get("timestamp"),
                "rainfall_mm": first_hazard.get("rainfall_mm"),
                "magnitude": first_hazard.get("magnitude"),
                "wind_speed": first_hazard.get("wind_speed"),
            }
            self.log("Flattened hazard info", flattened_hazard_info=flattened_hazard_info)

            context.session.state["hazard_info"] = flattened_hazard_info
            yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Hazard read successfully.")]))
        except (FileNotFoundError, json.JSONDecodeError, IndexError) as e:
            self.log(f"Error reading or parsing hazard_status.json: {e}", severity="ERROR")
            yield Event(author=self.name, content=genai_types.Content(parts=[genai_types.Part(text="Error reading hazard data.")]))

class HazardAgent(LoopAgent):
    """A loop agent that continuously monitors for hazards."""

    def __init__(self):
        super().__init__(
            name="HazardAgent",
            sub_agents=[HazardReaderAgent(name="HazardReaderAgent")],
            max_iterations=1, # The loop will be handled by the coordinator for now
        )
