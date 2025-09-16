import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.agent import root_agent
from google.genai import types as genai_types

async def main():
    """Runs the new agent architecture."""
    session_service = InMemorySessionService()
    user_id = "test_user"
    session = await session_service.create_session(app_name="crisisiq", user_id=user_id)
    session_id = session.id

    runner = Runner(agent=root_agent, app_name="crisisiq", session_service=session_service)
    # The run_async method requires a user_id and a new_message.
    # Since our process is not started by a user message, we can pass an empty message.
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=genai_types.Content(role="user", parts=[genai_types.Part(text="")])
    ):
        print(f"Event: {event.author}: {event.content}")
        if event.is_final_response():
            print("\n--- Crisis Response Summary ---")
            print(event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
