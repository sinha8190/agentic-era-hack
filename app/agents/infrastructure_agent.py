from app.agents.base import BaseAgent
import json

class InfrastructureAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="InfrastructureAgent",
            instruction="This agent provides information about infrastructure status.",
            tools=[],
        )

    def get_blocked_routes(self):
        """
        Reads the infrastructure status file and returns a list of blocked routes.
        """
        try:
            with open("app/data/infra_status.json") as f:
                infra_data = json.load(f)
            blocked_routes = infra_data.get("blocked_routes", [])
            self.log(f"Blocked routes: {blocked_routes}")
            return blocked_routes
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.log(f"Error reading or parsing infra_status.json: {e}", severity="ERROR")
            return []

infrastructure_agent = InfrastructureAgent()

def get_blocked_routes_tool():
    """
    A tool to get the list of blocked routes from the infrastructure agent.
    """
    return infrastructure_agent.get_blocked_routes()
