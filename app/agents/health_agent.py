from app.agents.base import BaseAgent
import google.generativeai as genai

class HealthAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="HealthAgent",
            instruction="This agent is responsible for health-related tasks.",
            tools=[],
        )

    async def handle_hazard(self, hazard_info):
        self.log(f"Received hazard info", hazard_info=hazard_info)
        hazard_type = hazard_info.get("hazard")

        prompt = "You are a triage doctor. Your task is to prioritize medical needs based on the hazard. You should also suggest where to setup medical camps and how to prioritize patients."

        if hazard_type.lower() == "flood":
            prompt += " The hazard is a flood. The most common issues are drowning and waterborne diseases."
        elif hazard_type.lower() == "earthquake":
            prompt += " The hazard is an earthquake. The most common issues are trauma, fractures, and crush injuries."
        elif hazard_type.lower() == "storm":
            prompt += " The hazard is a storm. The most common issues are hypothermia and wounds from flying debris."
        else:
            self.log(f"Unknown hazard type: {hazard_type}", severity="WARNING")
            # In a real scenario, we might want to return a more specific error or raise an exception.
            return "Unknown hazard type provided."

        prompt += " Explain the prioritization of medical needs in a concise manner."

        # It's a good practice to wrap external calls in a try-except block.
        try:
            model = genai.GenerativeModel(self.model)
            response = await model.generate_content_async(prompt)
            # Assuming the response object has a 'text' attribute.
            # Based on google-genai library.
            triage_report = response.text
            self.log(f"Generated triage report for {hazard_type}", triage_report=triage_report)
            return triage_report
        except Exception as e:
            self.log(f"Error generating triage report for {hazard_type}: {e}", severity="ERROR")
            return f"Error generating triage report: {e}"

