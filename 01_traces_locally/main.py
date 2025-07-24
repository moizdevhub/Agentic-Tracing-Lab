import os
from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, set_default_openai_api, set_default_openai_client, trace, set_trace_processors
from openai import AsyncOpenAI
from pprint import pprint
from agents.tracing.processor_interface import TracingProcessor
from dotenv import load_dotenv

load_dotenv()


gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")


#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

google_gemini_config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)


class LocalTraceProcessor(TracingProcessor):
    def __init__(self):
        self.traces = []
        self.spans = []
    
    def on_trace_start(self, trace):
        self.traces.append(trace)
        print(f"Trace Started {trace.trace_id}")
    
    def on_trace_end(self, trace):
        print(f"Trace Ended {trace.trace_id}")

    def on_span_start(self, span):
        self.spans.append(span)
        print(f"Span Started {span.span_id} ")
        print(f"Span Detail")
        print(f"{span.export()}")
    
    def on_span_end(self, span):
        print(f"Span Ended: {span.span_id}")
        print(f"Span Details")
        print(span.export())

    def force_flush(self):
        print(f"Forcing flush of trace Data")

    def shutdown(self):
        print(f"======shutting down Trace Processor========")
        print(f"Collected Traces")
        for trace in self.traces:
            print(trace.export())
        
        for span in self.spans:
            print(span.export())

set_default_openai_client(client=external_client,use_for_tracing=True)
set_default_openai_api("chat_completions")

local_processor = LocalTraceProcessor()
set_trace_processors([local_processor])

async def main():
     agent = Agent(name= "Example Agent", instructions="Perform Example Task", model= model)

     with trace("Example workflow"):
         first_result = await Runner.run(agent,"Start the task", run_config= google_gemini_config)
         second_result = await Runner.run(agent, f"Rate this result {first_result.final_output}",  run_config= google_gemini_config)
         print(f"Result: {first_result.final_output}")
         print(f"Rating {second_result.final_output}")

import asyncio
asyncio.run(main())