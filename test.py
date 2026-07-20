import asyncio
import os

from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()


async def main():
    agent = Agent(
        model=Gemini(
            id="gemini-3.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
    )

    response = await agent.arun("Say hello in one sentence.")
    print(response.content)


asyncio.run(main())
