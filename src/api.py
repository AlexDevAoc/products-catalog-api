from fastapi import FastAPI
from src.auth.controller import router as auth_router
from src.users.controller import router as users_router
from src.roles.controller import router as roles_router
from src.permissions.controller import router as permissions_router
from src.user_change_logs.controller import router as user_change_logs_router
from src.user_sessions.controller import router as user_sessions_router
from src.brands.controller import router as brands_router
from src.products.controller import router as products_router
from src.product_views.controller import router as product_views_router
from src.product_change_logs.controller import router as product_change_logs_router
from src.admin_notifications.controller import router as admin_notifications_router
from src.health.controller import router as health_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(roles_router)
    app.include_router(permissions_router)
    app.include_router(user_change_logs_router)
    app.include_router(user_sessions_router)
    app.include_router(brands_router)
    app.include_router(products_router)
    app.include_router(product_views_router)
    app.include_router(product_change_logs_router)
    app.include_router(admin_notifications_router)
    app.include_router(health_router)