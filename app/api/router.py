from fastapi import APIRouter
from app.api.routes import auth, admin_users, admin_vault, vault, fill,admin_panel

api_router = APIRouter()
from app.api.routes import vault_v2

api_router.include_router(vault_v2.router)
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(admin_users.router, prefix="/admin", tags=["Admin Users"])
api_router.include_router(admin_vault.router, prefix="/admin", tags=["Admin Vault"])
api_router.include_router(vault.router, prefix="/vault", tags=["Vault"])
api_router.include_router(fill.router, prefix="/fill", tags=["Fill"])
api_router.include_router(admin_panel.router, tags=["Admin Panel"])