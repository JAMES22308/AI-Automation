
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





# -----------------------------
# General AI chat endpoint
# -----------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    # Get Gemini API key from .env
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing"
        )

    # AI models to try in order
    models = [
        "gemini-3.5-flash",
        "gemini-2.5-flash-lite"
    ]

    # Prompt sent to Gemini
    prompt = f"""
    You are a helpful AI assistant.

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

    # Request headers
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    # Store the last error in case every model fails
    last_error = None

    # Try each model
    for model in models:

        print(f"Trying Gemini model: {model}")

        # Gemini API endpoint
        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model}:generateContent"
        )

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

        # Retry temporary failures twice
        for attempt in range(2):

            try:

                response = requests.post(
                    url,
                    headers=headers,
                    json=body,
                    timeout=30
                )

            except requests.RequestException as error:

                print(
                    f"{model} connection error:",
                    repr(error)
                )

                last_error = str(error)

                # Move to the next model
                break

            print(
                f"{model} status:",
                response.status_code
            )

            # -----------------------------
            # Successful response
            # -----------------------------

            if response.status_code == 200:

                try:

                    data = response.json()

                    ai_text = (
                        data["candidates"][0]
                        ["content"]["parts"][0]["text"]
                    )

                except (
                    ValueError,
                    KeyError,
                    IndexError,
                    TypeError
                ):

                    print(
                        f"Unexpected response from {model}:",
                        response.text
                    )

                    last_error = (
                        f"Unexpected response from {model}."
                    )

                    break

                print(
                    f"Gemini response from {model}:"
                )

                print(ai_text)

                return {
                    "response": ai_text
                }

            # -----------------------------
            # Quota exceeded
            # -----------------------------

            if response.status_code == 429:

                print(
                    f"{model} quota exceeded."
                )

                last_error = (
                    f"{model} quota exceeded."
                )

                # Do not retry an exhausted model.
                # Immediately try the next model.
                break

            # -----------------------------
            # Temporary Gemini error
            # -----------------------------

            if response.status_code == 503:

                print(
                    f"{model} temporarily unavailable."
                )

                last_error = (
                    f"{model} temporarily unavailable."
                )

                if attempt < 1:

                    print(
                        f"Retrying {model}..."
                    )

                    time.sleep(2)

                    continue

                # Both attempts failed.
                # Move to the next model.
                break

            # -----------------------------
            # Other Gemini error
            # -----------------------------

            print(
                f"{model} error:",
                response.text
            )

            last_error = (
                f"{model} returned "
                f"status {response.status_code}."
            )

            # Move to the next model
            break

    # -----------------------------
    # All models failed
    # -----------------------------

    raise HTTPException(
        status_code=503,
        detail=(
            "All AI models are currently unavailable. "
            f"Last error: {last_error}"
        )
    )