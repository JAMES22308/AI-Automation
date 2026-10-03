
import time
import os
import json
import requests

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

app = FastAPI()


# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Request formats
# -----------------------------

class TaskRequest(BaseModel):
    task_text: str


class ChatRequest(BaseModel):
    message: str


# -----------------------------
# Home / test endpoint
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Python AI service is running smoothly"
    }


# -----------------------------
# AI task analysis endpoint
# -----------------------------

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

    # Try Gemini up to 3 times if temporarily unavailable
    # response = None

    # for attempt in range(3):

    #     try:
    #         response = requests.post(
    #             url,
    #             headers=headers,
    #             json=body,
    #             timeout=30
    #         )

    #     except requests.RequestException as error:

    #         print("Request error:", error)

    #         if attempt < 2:
    #             print(f"Retrying... {attempt + 1}/3")
    #             time.sleep(2)
    #             continue

    #         raise HTTPException(
    #             status_code=503,
    #             detail="Unable to connect to Gemini API."
    #         )

    #     print("Gemini status:", response.status_code)

    #     # Successful response
    #     if response.status_code == 200:
    #         break

    #     # Gemini temporarily unavailable
    #     if response.status_code == 503 and attempt < 2:

    #         print(
    #             f"Gemini temporarily unavailable. "
    #             f"Retrying... {attempt + 2}/3"
    #         )

    #         time.sleep(2)
    #         continue

    #     # Other API error or all retries failed
    #     print("Gemini error:", response.text)

    #     raise HTTPException(
    #         status_code=response.status_code,
    #         detail=f"Gemini API error: {response.text}"
    #     )



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

            print("Gemini connection error:", repr(error))

            if attempt < 2:
                print(f"Retrying... {attempt + 1}/3")
                time.sleep(2)
                continue

            raise HTTPException(
                status_code=503,
                detail=f"Unable to connect to Gemini API: {error}"
            )

        print("Gemini status:", response.status_code)

        if response.status_code == 200:
            break

        if response.status_code == 503 and attempt < 2:

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying... {attempt + 2}/3"
            )

            time.sleep(2)
            continue

        print("Gemini error:", response.text)

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Gemini API error: {response.text}"
        )










    # Convert Gemini response into Python data
    try:
        data = response.json()

    except ValueError:

        print(
            "Gemini returned invalid JSON:",
            response.text
        )

        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid response."
        )

    # Extract Gemini's generated text
    try:
        ai_text = data["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError, TypeError):

        print(
            "Unexpected Gemini response:",
            data
        )

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

    # Validate required fields
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
    if analysis["priority"] not in [
        "High",
        "Medium",
        "Low"
    ]:

        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid priority."
        )

    # Return final result
    return {
        "task": task.task_text,
        "priority": analysis["priority"],
        "category": analysis["category"],
        "suggestion": analysis["suggestion"]
    }







# -----------------------------
# General AI chat endpoint
# -----------------------------
# -----------------------------
# General AI chat endpoint
# -----------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not gemini_api_key and not groq_api_key:
        raise HTTPException(
            status_code=500,
            detail="No AI provider API keys are configured."
        )

    prompt = f"""
You are Lexia, an AI assistant created by Michael James Soria.

Your name is Lexia.

If the user asks who you are, what your name is, who created you,
who made you, who developed you, who built you, who owns you,
or asks any similar question about your identity or creator,
identify yourself as Lexia and state that you were created by
Michael James Soria.

Do not claim that Michael James Soria personally trained the
underlying AI model. Lexia is an AI application created by
Michael James Soria and powered by external AI models.

Answer the user's request clearly and accurately.

You can help with:
- General questions
- Programming
- Code generation
- Debugging
- Explanations
- Writing
- Task planning
- Technical questions
- Data analysis
- Comparisons

If the user asks for programming code:
- Provide working code.
- Use the programming language requested.
- Format code using markdown code blocks.
- Briefly explain the code when useful.

Use Markdown formatting when appropriate.

User request:

{request.message}
"""

    # -----------------------------
    # 1. Try Gemini first
    # -----------------------------

    if gemini_api_key:

        gemini_url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-3.5-flash:generateContent"
        )

        gemini_headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": gemini_api_key
        }

        gemini_body = {
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

        try:

            response = requests.post(
                gemini_url,
                headers=gemini_headers,
                json=gemini_body,
                timeout=30
            )

            print(
                "Gemini status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                ai_text = (
                    data["candidates"][0]
                    ["content"]["parts"][0]["text"]
                )

                print("Response generated by Gemini")

                return {
                    "response": ai_text,
                    "provider": "gemini"
                }

            print(
                "Gemini unavailable:",
                response.status_code,
                response.text
            )

        except requests.RequestException as error:

            print(
                "Gemini connection error:",
                repr(error)
            )

    # -----------------------------
    # 2. Fallback to Groq
    # -----------------------------

    if groq_api_key:

        groq_url = (
            "https://api.groq.com/openai/v1/chat/completions"
        )

        groq_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {groq_api_key}"
        }

        groq_body = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. "
                        "Answer clearly and accurately."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:

            response = requests.post(
                groq_url,
                headers=groq_headers,
                json=groq_body,
                timeout=30
            )

            print(
                "Groq status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                ai_text = (
                    data["choices"][0]
                    ["message"]["content"]
                )

                print("Response generated by Groq")

                return {
                    "response": ai_text,
                    "provider": "groq"
                }

            print(
                "Groq error:",
                response.status_code,
                response.text
            )

        except requests.RequestException as error:

            print(
                "Groq connection error:",
                repr(error)
            )

    # -----------------------------
    # 3. Both providers failed
    # -----------------------------

    raise HTTPException(
        status_code=503,
        detail="All AI providers are currently unavailable."
    )