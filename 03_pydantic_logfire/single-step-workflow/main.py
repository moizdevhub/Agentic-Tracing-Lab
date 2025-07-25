from agents import Agent, Runner, trace
from pydantic import BaseModel
from logfire import Logfire
from typing import Dict, Any
from setup_config import google_gemini_config,model
import time
import asyncio

class AgentLog(BaseModel):
    agent_name:str
    input: str
    output:str
    Metadata:Dict[str,Any]
    processing_time:float
    token_used:int

async def main():
    log_fire = Logfire()

    agent = Agent(
        name="Code Generater", instructions="Generate Python Code Based on requirments", model=model
    )
    
    with trace("Code Generation workflow") as gen_trace:
        start_time = time.time()

        result = await Runner.run(agent,"write a fuction to calculate factorial", run_config=google_gemini_config)

        log_end = AgentLog(
            agent_name= agent.name,
            input="write a function to calculate factorial",
            output=result.final_output,
            Metadata={
                "complexity": "medium",
                "language":"python",
                "model": "gemini-2.0-flash"
            },
            processing_time= time.time() - start_time,
            token_used = getattr(getattr(result, "usage", {}), "total_tokens", 0)
            # token_used= result.usage.total_tokens

        )

        await log_fire.log(log_end)
        print(f"Generate Code :{result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())