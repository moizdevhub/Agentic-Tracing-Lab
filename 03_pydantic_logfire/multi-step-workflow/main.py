from agents import Agent, Runner, trace
from pydantic import BaseModel
from logfire import Logfire
from typing import List, Dict, Any
from setup_config import google_gemini_config, model
import time

class WorkflowStep(BaseModel):
    step_name: str
    input: str
    output: str
    duration: float
    metadata: Dict[str, Any]

class WorkflowLog(BaseModel):
    workflow_id: str  
    steps: List[WorkflowStep]  
    total_duration: float
    status: str

async def main():
    Log_fire = Logfire()

    code_agent = Agent(
        name="Code Generator",
        instructions="Generate Python code based on requirements.",
        model=model
    )

    test_agent = Agent(
        name="Test Generator",
        instructions="Generate Unit Test for Python code.",
        model=model
    )

    with trace("Code and Test Generation workflow") as workflow_trace:
        workflow_start = time.time()
        steps = []

        # ✅ Code generation step
        code_start = time.time()
        code_result = await Runner.run(code_agent, "write a function to calculate fibonacci numbers")

        steps.append(WorkflowStep(
            step_name="code_generation",
            input="write a function to calculate fibonacci number",
            output=code_result.final_output,
            duration=time.time() - code_start,
            metadata={"complexity": "medium"}
        ))

        # ✅ Test generation step
        test_start = time.time()
        test_result = await Runner.run(
            test_agent,
            f"write unit test for this code: {code_result.final_output}.",
            run_config=google_gemini_config
        )

        steps.append(WorkflowStep(
            step_name="test_generation",
            input=f"write a unit test for this code: {code_result.final_output}",
            output=test_result.final_output,
            duration=time.time() - test_start,
            metadata={"test_count": 3}
        ))

        # ✅ Final workflow log
        workflow_log = WorkflowLog(
            workflow_id=workflow_trace.id,
            steps=steps,
            total_duration=time.time() - workflow_start,
            status="completed"
        )

        await Log_fire.log(workflow_log)

        print(f"Generated code: {code_result.final_output}")
        print(f"Generated test: {test_result.final_output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
