from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):

        self.connections = []

    async def connect(self, websocket: WebSocket):

        await websocket.accept()

        self.connections.append(websocket)

    async def disconnect(self, websocket):

        if websocket in self.connections:

            self.connections.remove(websocket)

    async def broadcast(self, data):

        disconnected = []

        for ws in self.connections:

            try:

                await ws.send_json(data)

            except Exception:

                disconnected.append(ws)

        for ws in disconnected:

            self.connections.remove(ws)

manager = ConnectionManager()

@property
def count(self):

    return len(self.connections)