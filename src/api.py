from fastapi import FastAPI
from src.auth.controller import router as auth_router
from src.users.controller import router as users_router
from src.roles.controller import router as roles_router
from src.permissions.controller import router as permissions_router
from src.user_change_logs.controller import router as user_change_logs_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(roles_router)
    app.include_router(permissions_router)
    app.include_router(user_change_logs_router)