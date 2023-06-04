import json

import redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.requests import Request
from fastapi.responses import Response, RedirectResponse, HTMLResponse

from service import hash_password

app = FastAPI()
templates = Jinja2Templates(directory="templates")


redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket):
        for connection in self.active_connections:
            if websocket != connection:
                await connection.send_text(message)


manager = ConnectionManager()


@app.get('/register')
async def register(request: Request,):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def postdata(request: Request, name: str = Form(...), password: str = Form(...), email: str = Form(...)):
    if not redis_client.exists(name):
        data = {
            'password': hash_password(password),
            'email': email
        }
        redis_client.hmset(name, data)
    else:
        raise HTTPException(status_code=400, detail="User already exists")
    return HTMLResponse(
        content='User registered successfully, <p>Click <a href="/login">here</a> to enter login page</p>',
        status_code=200
    )


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {'request': request})


@app.post("/login")
async def post_login(request: Request, response: Response, name: str = Form(...), password: str = Form(...)):
    if redis_client.exists(name):
        if redis_client.hgetall(name).get('password') == hash_password(password):
            response_redirect = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
            response_redirect.set_cookie(key='user_name', value=name)
            return response_redirect
        raise HTTPException(status_code=400, detail="Password is not correct")
    raise HTTPException(status_code=400, detail="User is not registered")


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("enter.html", {"request": request})


@app.get("/{room_name}")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/{client_name}")
async def websocket_endpoint(websocket: WebSocket, client_name: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_name} says: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_name} left the chat")
