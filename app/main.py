from fastapi import FastAPI, UploadFile, Form
from langchain_core.messages import HumanMessage, AIMessage
from app.graph import agent
from app.utils.excel import read_excel, apply_actions
from app.schemas.request import Request
app = FastAPI()

@app.post("/api/process")
async def process(request: Request): #file: UploadFile = None
    temp_path = f"app/files/dummy_sheet.xlsm"
    metadata = read_excel(temp_path)
    inputs = {
        "messages": [HumanMessage(content=request.message)],  
        "metadata": metadata, 
        "file_path": temp_path
    }
    result = await agent.ainvoke(input=inputs)

    ai_message = None
    for msg in reversed(result.get("messages", [])):
        if isinstance(msg, AIMessage):
            ai_message = msg.content
            break

    return {"message": ai_message}
    #return {"actions": actions, "file_path": temp_path}
