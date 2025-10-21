# excel-agent




activate venv 
source venv/bin/activate


pip install fastapi uvicorn langchain langchain-google-genai langgraph openpyxl pandas python-dotenv pydantic


uvicorn app.main:app --reload
