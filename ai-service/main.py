# test
import os
import json
import requests

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()


class TaskRequest(BaseModel):
    task_text: str


@app.get("/")
def home():
    return {
        "message": "Python AI service is running"
    }


@app.post("/analyse")
def analyse(task: TaskRequest):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "error": "GEMINI_API_KEY is missing"
        }

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.5-flash:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

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

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    print("Gemini status:", response.status_code)

    if response.status_code != 200:
        print("Gemini error:", response.text)

        return {
            "error": "Gemini API request failed",
            "details": response.text
        }

    data = response.json()

    try:
        ai_text = data["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError):
        print("Unexpected Gemini response:", data)

        return {
            "error": "Unexpected Gemini response",
            "details": data
        }

    print("Gemini response:")
    print(ai_text)

    try:
        analysis = json.loads(ai_text)

        return {
            "task": task.task_text,
            "priority": analysis["priority"],
            "category": analysis["category"],
            "suggestion": analysis["suggestion"]
        }

    except (json.JSONDecodeError, KeyError):

        print("JSON parsing failed.")

        return {
            "error": "AI returned invalid JSON",
            "raw_response": ai_text
        }

