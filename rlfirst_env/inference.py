import os
import json
from openai import OpenAI
from typing import List

# Import our local environment and models
from env import InventoryEnv
from models import InventoryAction

# --- EXACT MATCH TO CHECKLIST SCREENSHOT ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")
# -------------------------------------------

TASK_NAME = "E-commerce Restock"
BENCHMARK = "OpenEnv Hackathon"
MAX_STEPS = 5
SUCCESS_SCORE_THRESHOLD = 0.9

# --- MANDATORY LOGGING STRUCTURE ---
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str = None):
    err_str = f" error={error}" if error else ""
    print(f"[STEP] step={step} action='{action}' reward={reward} done={done}{err_str}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    print(f"[END] success={success} steps={steps} score={score} rewards={rewards}", flush=True)

# Because we swapped to the synchronous OpenAI client to match the checklist, 
# we need to wrap the async environment calls in a synchronous runner
import asyncio

async def run_environment():
    # Use HF_TOKEN if available, otherwise fallback so local tests don't crash
    api_key = HF_TOKEN if HF_TOKEN else "mock-key"
    client = OpenAI(base_url=API_BASE_URL, api_key=api_key)
    
    # Initialize our environment
    env = InventoryEnv()

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset environment to get Task 1
        result = await env.reset()
        last_echoed = result.observation.echoed_message
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            system_prompt = """You are an AI Inventory Manager. 
            Based on the message from the environment, choose ONE action to solve the problem.
            You must output ONLY valid JSON matching this schema exactly:
            {"action_type": "check_inventory" | "order_stock" | "update_price", "sku": "string", "quantity": int, "price": float}
            If a field is not needed, output null for it. Do not include markdown formatting."""
            
            user_prompt = f"System Message: {last_echoed}\nPast Actions: {history}"

            try:
                # Call the LLM using the required OpenAI client
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                action_dict = json.loads(response.choices[0].message.content)
                action = InventoryAction(**action_dict)
                action_str = str(action_dict).replace('\n', '')
                
            except Exception as e:
                # Fallback action if LLM fails (e.g. no valid API key)
                action = InventoryAction(action_type="check_inventory")
                action_str = "Fallback: check_inventory"

            # Execute the action in the environment
            result = await env.step(action)
            obs = result.observation

            reward = result.reward or 0.0
            done = result.done
            error = None

            rewards.append(reward)
            steps_taken = step
            last_echoed = obs.echoed_message

            log_step(step=step, action=action_str, reward=reward, done=done, error=error)
            history.append(f"Action: {action_str} -> Reward: {reward}")

            if done:
                break

        score = sum(rewards) 
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(run_environment())