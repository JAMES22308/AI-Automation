# python
import time
import os
import json
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

app = FastAPI()


# Request format
class TaskRequest(BaseModel):
    task_text: str


# Home/test endpoint
@app.get("/")
def home():
    return {
        "message": "Python AI service is running"
    }


# AI task analysis endpoint
@app.post("/analyse")
def analyse(task: TaskRequest):

    # Get Gemini API key from .env
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing"
        )

    # Gemini API endpoint
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash:generateContent"
    )

    # Request headers
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    # Prompt sent to Gemini
    prompt = f"""
Analyse this task:

{task.task_text}

Return ONLY valid JSON.

Use exactly these fields:

{{
    "priority": "High",
    "category": "Education",
    "suggestion": "A short helpful suggestion"
}}

Priority must be exactly one of:
High, Medium, Low.

Do not use markdown.
Do not add ```json.
Do not add any text before or after the JSON.
"""

    # Request body
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # Try Gemini up to 3 times if the service temporarily returns 503
    response = None

    for attempt in range(3):

        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                timeout=30
            )

        except requests.RequestException as error:
            print("Request error:", error)

            if attempt < 2:
                print(f"Retrying... {attempt + 1}/3")
                time.sleep(2)
                continue

            raise HTTPException(
                status_code=503,
                detail="Unable to connect to Gemini API."
            )

        print("Gemini status:", response.status_code)

        # Successful response
        if response.status_code == 200:
            break

        # Gemini temporarily unavailable
        # Gemini temporarily unavailable
        if response.status_code == 503 and attempt < 2:
            print(
                f"Gemini temporarily unavailable. "
                f"Retrying... {attempt + 2}/3"
            )

            time.sleep(2)
            continue

        # Other API error or all retries failed
        print("Gemini error:", response.text)

        raise HTTPException(
            status_code=response.status_code,
            detail="Gemini API request failed"
        )

    # Convert Gemini response into Python data
    try:
        data = response.json()

    except ValueError:
        print("Gemini returned invalid JSON:", response.text)

        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid response."
        )

    # Extract Gemini's generated text
    try:
        ai_text = data["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError, TypeError):
        print("Unexpected Gemini response:", data)

        raise HTTPException(
            status_code=502,
            detail="Unexpected response received from Gemini."
        )

    print("Gemini response:")
    print(ai_text)

    # Convert Gemini's JSON text into Python dictionary
    try:
        analysis = json.loads(ai_text)

    except json.JSONDecodeError:
        print("JSON parsing failed.")
        print("Raw response:", ai_text)

        raise HTTPException(
            status_code=502,
            detail="Gemini returned invalid JSON."
        )

    # Validate the fields returned by Gemini
    required_fields = [
        "priority",
        "category",
        "suggestion"
    ]

    for field in required_fields:

        if field not in analysis:
            raise HTTPException(
                status_code=502,
                detail=f"Gemini response is missing '{field}'."
            )

    # Validate priority
    if analysis["priority"] not in ["High", "Medium", "Low"]:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid priority."
        )

    # Return final result to the client
    return {
        "task": task.task_text,
        "priority": analysis["priority"],
        "category": analysis["category"],
        "suggestion": analysis["suggestion"]
    }

