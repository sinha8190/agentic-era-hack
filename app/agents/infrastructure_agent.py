from app.agents.base import BaseAgent
import json
from app.utils.tracing import logger
import os
import requests

class InfrastructureAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="InfrastructureAgent",
            instruction="This agent provides information about infrastructure status.",
            tools=[],
        )

    @staticmethod
    def get_blocked_routes():
        """
        Reads the infrastructure status file and returns a list of blocked routes.
        """
        api_key = "AIzaSyClXak4EIxm7Bi2exOyC8Z7A9wdqFIhTg8"
        if api_key:
            # Placeholder for Google Roads API call
            logger.log_struct({"message": "Using Google Roads API to get blocked routes."})
            # In a real implementation, you would make a request to the Google Roads API
            # and parse the response to get the blocked routes.
            # For this example, we will return an empty list.
            return []
        else:
            logger.log_struct({"message": "Google Roads API key not found. Defaulting to roads.json."})
            try:
                with open("app/data/roads.json") as f:
                    roads_data = json.load(f)
                blocked_routes = [road["name"] for road in roads_data.get("roads", []) if road.get("status") == "closed"]
                logger.log_struct({"message": "Retrieved blocked routes from roads.json", "blocked_routes": blocked_routes})
                return blocked_routes
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.log_struct({"message": f"Error reading or parsing roads.json: {e}"}, severity="ERROR")
                return []

def get_blocked_routes_tool():
    """
    A tool to get the list of blocked routes from the infrastructure agent.
    """
    return InfrastructureAgent.get_blocked_routes()
