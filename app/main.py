import json
from typing import AsyncGenerator
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from app.graph import agent
from app.utils.excel import read_excel, apply_actions
from app.schemas.request import Request
app = FastAPI()

@app.post("/api/process")
async def process(request: Request): #file: UploadFile = None
    temp_path = f"app/files/dummy_sheet.xlsm"
    metadata = read_excel(temp_path)
    """ 
    result = await agent.ainvoke(input=inputs)

    ai_message = None
    for msg in reversed(result.get("messages", [])):
        if isinstance(msg, AIMessage):
            ai_message = msg.content
            break 
    
    return {"message": ai_message}    
    """

    async def event_generator() -> AsyncGenerator[str, None]:
            """
            Gera eventos SSE a partir do agente, usando `stream_mode="updates"`.
            Cada pedaço enviado contém a última mensagem do assistente.
            """

            inputs = {
                "messages": [HumanMessage(content=request.message)],  
                "metadata": metadata, 
                "file_path": temp_path
            }

            async for stream_mode, chunk in agent.astream(inputs, stream_mode=["updates", "custom"]):
                if stream_mode == "updates":
                    for step, data in chunk.items():

                        if not data or "messages" not in data:
                            continue

                        for msg in data["messages"]:
                            if isinstance(msg, AIMessage) and msg.content:
                                payload = json.dumps({
                                    "type": "assistant_message" ,
                                    "content": msg.content
                                })
                                yield f"data: {payload}\n\n"

                elif stream_mode == "custom":   
                    payload = json.dumps({
                        "type": "token",
                        "content": chunk
                    })
                    yield f"data: {payload}\n\n" 

            # Finaliza o stream
            yield "data: [DONE]\n\n"

    # Retorna a resposta como SSE
    return StreamingResponse(event_generator(), media_type="text/event-stream")
    #return {"actions": actions, "file_path": temp_path}
