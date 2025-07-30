from agents import Agent, Runner, trace
import agentops
from dotenv import load_dotenv
from setup_config import model,google_gemini_config
import os

load_dotenv()

AgentOps_key = os.getenv("AGENTOPS_API_KEY")
OpenAI_key = os.getenv("OPENAI_API_KEY")
Gemeni_Key = os.getenv("GEMINI_API_KEY")



async def main():

    if not AgentOps_key:
       raise ValueError("Missing AGENTOPS_API_KEY")
    if not OpenAI_key:
       raise ValueError("Missing OPENAI_API_KEY")


    # Initialize AgentOps
    agent_ops = agentops(AgentOps_key)
    
    # Create an agent
    agent = Agent(
        name="Code Reviewer",
        instructions="Review code and suggest improvements.",
        model= model
    )

    # Create a trace for the code review workflow
    with trace("Code Review Workflow") as review_trace:
        # Start monitoring the agent
        with agent_ops.monitor():
            # Run the agent
          try:
            result = await Runner.run(
               agent, "Review this code: def process_data(data): return data.strip()", run_config=google_gemini_config)
            
             # Log metrics
            agent_ops.log_metric("code_complexity", "low")
            agent_ops.log_metric("review_duration", 2.5)
            agent_ops.log_metric("suggestions_count", 3)
            
            print(f"Review: {result.final_output}")
          
          except Exception as e:
            print(f"Agent failed: {e}")
            agent_ops.log_metric("error", str(e))
            return

            
           

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())