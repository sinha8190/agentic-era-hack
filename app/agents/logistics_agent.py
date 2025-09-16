from app.agents.base import BaseAgent
from app.agents.infrastructure_agent import get_blocked_routes_tool
import google.generativeai as genai

class LogisticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="LogisticsAgent",
            instruction="This agent is responsible for managing logistics, including resource allocation and transport planning.",
            tools=[get_blocked_routes_tool],
        )

    async def handle_hazard(self, hazard_info):
        self.log(f"Received hazard info: {hazard_info}")
        hazard_type = hazard_info.get("hazard")

        # 1. LLM-based resource triage
        prompt = f"You are a logistics expert. For a '{hazard_type}' hazard, what are the essential resources to deploy? Be specific."
        
        try:
            model = genai.GenerativeModel(self.model)
            response = await model.generate_content_async(prompt)
            resource_list = response.text
        except Exception as e:
            self.log(f"Error generating resource list: {e}", severity="ERROR")
            resource_list = f"Could not determine resources for {hazard_type}."

        # 2. Get blocked routes from infrastructure agent
        blocked_routes = get_blocked_routes_tool()

        # 3. Consolidate response
        consolidated_response = f"""
        Logistics Plan for {hazard_type}:
        
        Resources to Deploy:
        {resource_list}
        
        Transport Plan:
        Planning transport of resources, avoiding the following blocked routes: {', '.join(blocked_routes) if blocked_routes else 'None'}.
        """

        self.log(consolidated_response)
        return consolidated_response

logistics_agent = LogisticsAgent()
