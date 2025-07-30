
from agents import Agent ,Runner, trace
from agentops import AgentOps

async def main():
    agent_ops = AgentOps()

    code_agent = Agent(
        name="Code Generator" , instructions = "Generate a code based on python."
    )

    test_agent = Agent(
        name="Test Generator", instructions="Generate a unit test."
    )


    with trace("Code and Test Generate workflow"):
        with agent_ops.monitor():
            code_result = await Runner(code_agent, "write a function to calculate factorial")

            agent_ops.log_metric("code_complexity", "medium")
            agent_ops.log_metric("code_lenght", len(code_result.final_output))
            
            test_result = await Runner(test_agent,f"wirte a unit test of {code_result.final_output}")

            agent_ops.log_metric("test_count", 3)
            agent_ops.log_metric("test_coverage",0.95)

            print(f"Generate Code: {code_result.final_output}")
            print(f"Genrate  Test: {test_result.final_output}")

            metrics = agent_ops.get_metrics()
            print(f"Performance Metrics: {metrics}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())