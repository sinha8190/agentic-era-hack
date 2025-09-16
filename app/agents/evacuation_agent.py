from app.agents.base import BaseAgent
from app.agents.infrastructure_agent import get_blocked_routes_tool
import json

class EvacuationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EvacuationAgent",
            instruction="This agent is responsible for planning and managing evacuation routes based on real-time road status.",
            tools=[get_blocked_routes_tool],
        )

    def _find_evacuation_routes(self):
        """
        Finds safe evacuation routes from hazard zones to shelters based on open roads and blocked routes.
        """
        blocked_routes = get_blocked_routes_tool()
        
        try:
            with open("app/data/roads.json") as f:
                roads_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.log(f"Error reading or parsing roads.json: {e}", severity="ERROR")
            return "Could not generate evacuation plan due to missing or invalid road data."

        open_roads = [road for road in roads_data.get("roads", []) if road.get("status") == "open" and road.get("name") not in blocked_routes]
        hazard_zones = roads_data.get("hazard_zones", [])
        
        evacuation_routes = []
        for zone in hazard_zones:
            for road in open_roads:
                if road.get("from") == zone:
                    evacuation_routes.append(f"From {zone}, take {road['name']} to {road['to']}.")
        
        if not evacuation_routes:
            return "No safe evacuation routes found."
            
        return "Evacuation Plan:\n" + "\n".join(evacuation_routes)

    def handle_hazard(self, hazard_info):
        self.log(f"Received hazard info: {hazard_info}")
        hazard_type = hazard_info.get("hazard")

        if hazard_type not in ["Flood", "Storm"]:
            self.log(f"Evacuation not typically required for {hazard_type}.")
            return f"Evacuation not activated for {hazard_type}."

        evacuation_plan = self._find_evacuation_routes()
        self.log(evacuation_plan)
        return evacuation_plan

evacuation_agent = EvacuationAgent()
