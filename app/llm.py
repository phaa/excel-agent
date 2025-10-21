import os
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()

def load_llm():
	model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
	return ChatGoogleGenerativeAI(
		api_key=os.getenv("GEMINI_API_KEY"),
		model=model_name,
		temperature=0.0,
		max_tokens=None,
		timeout=None,
		max_retries=2,
	)