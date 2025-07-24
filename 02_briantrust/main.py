# main.py
import os
import asyncio
from braintrust import Eval
from autoevals import Levenshtein
from agents import Agent, Runner
from setup_config import model, google_gemini_config # Assuming this correctly imports your setup
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("BRAINTRUST_API_KEY") # Ensure BRAINTRUST_API_KEY is set in your .env

agent = Agent(name="Code Evaluator", model=model, instructions="Review code quality and improvements")

# --- IMPORTANT CHANGE HERE ---
# Modify sync_runner to return only the final_output string, not the whole RunResult object.
def sync_runner(agent, input_text): # Renamed 'input' to 'input_text' to avoid shadowing built-in
    runner = Runner()
    run_result = asyncio.run(runner.run(agent, input_text, run_config=google_gemini_config))
    return run_result.final_output # <--- Return only the string output

# Now, the Eval's task function will receive and log the JSON-serializable string
Eval(
    "Agent Code Review",
    data=[
        {
            "input": "def main(a,b): return a+b",
            "expected": "Looks good but lacks type hints."
        }
    ],
    task=lambda input_val: sync_runner(agent, input_val), # Use input_val here
    scores=[Levenshtein],
)