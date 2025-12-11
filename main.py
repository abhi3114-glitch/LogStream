from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
from typing import List, Optional
from backend.storage import LogStorage
from backend.ingestor import LogIngestor
import json

app = FastAPI(title="LogStream")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Core Components
storage = LogStorage(max_size=10000)
ingestor = LogIngestor(storage, udp_port=9000, tcp_port=9001)

@app.on_event("startup")
async def startup_event():
    await ingestor.start()

@app.on_event("shutdown")
async def shutdown_event():
    await ingestor.stop()

@app.get("/")
async def get():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/logs")
async def search_logs(
    query: Optional[str] = None,
    level: Optional[str] = None,
    service: Optional[str] = None,
    limit: int = 100
):
    return storage.search(query, level, service, limit)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Store filters for this connection
    filters = {
        "query": None,
        "level": None,
        "service": None
    }
    
    async def log_listener(log_entry):
        # Apply connection-specific filters before sending
        if filters["level"] and log_entry.get("level") != filters["level"]:
            return
        if filters["service"] and log_entry.get("service") != filters["service"]:
            return
        if filters["query"] and filters["query"].lower() not in log_entry.get("raw", "").lower():
            return
            
        try:
            await websocket.send_json({"type": "new_log", "data": log_entry})
        except Exception:
            # Connection likely closed
            pass

    storage.subscribe(log_listener)
    
    try:
        while True:
            # Receive commands from client (e.g., to update filters)
            data = await websocket.receive_json()
            if data.get("type") == "update_filters":
                new_filters = data.get("filters", {})
                filters.update(new_filters)
                
                # Resend recent logs matching new filters
                recent_logs = storage.search(
                    query=filters["query"],
                    level=filters["level"],
                    service=filters["service"],
                    limit=50
                )
                await websocket.send_json({"type": "history", "data": recent_logs})
                
    except WebSocketDisconnect:
        storage.unsubscribe(log_listener)
    except Exception as e:
        print(f"WS Error: {e}")
        storage.unsubscribe(log_listener)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
