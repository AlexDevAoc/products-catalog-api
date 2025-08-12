from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from src.auth.service import get_password_hash
from src.entities.user import User
from src.entities.role import Role
from src.entities.user_role import UserRole
from src.entities.brand import Brand

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASS = "Admin123!"


def seed_admin_and_brand(db: Session):
    # Role
    admin_role = db.query(Role).filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Admin role")
        db.add(admin_role); db.commit(); db.refresh(admin_role)
    # User
    admin_user = db.query(User).filter_by(email=ADMIN_EMAIL).first()
    if not admin_user:
        admin_user = User(email=ADMIN_EMAIL, first_name="Admin", last_name="User", password=get_password_hash(ADMIN_PASS))
        db.add(admin_user); db.commit(); db.refresh(admin_user)
    # Link role
    user_role = db.query(UserRole).filter_by(user_id=admin_user.id, role_id=admin_role.id).first()
    if not user_role:
        db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id)); db.commit()
    # Brand
    brand = db.query(Brand).filter_by(name="BrandX").first()
    if not brand:
        brand = Brand(name="BrandX", description="Test brand")
        db.add(brand); db.commit(); db.refresh(brand)
    return admin_user, brand


def login(client: TestClient):
    resp = client.post("/auth/token", data={"username": ADMIN_EMAIL, "password": ADMIN_PASS})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_product(client: TestClient, db_session: Session):
    admin, brand = seed_admin_and_brand(db_session)
    headers = login(client)
    payload = {
        "sku": "SKU-1",
        "name": "Producto 1",
        "description": "Desc",
        "price": 10.50,
        "brand_id": brand.id,
        "status": True
    }
    resp = client.post("/products/", json=payload, headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["sku"] == "SKU-1"
    assert data["name"] == "Producto 1"
    assert data["created_by"] == admin.id


def test_update_product_change_name(client: TestClient, db_session: Session):
    _, brand = seed_admin_and_brand(db_session)
    headers = login(client)
    # Crear producto
    payload = {
        "sku": "SKU-2",
        "name": "Prod 2",
        "description": "Desc2",
        "price": 20.00,
        "brand_id": brand.id,
        "status": True
    }
    resp = client.post("/products/", json=payload, headers=headers)
    assert resp.status_code == 200
    product_id = resp.json()["id"]
    # Update
    upd = {"name": "Prod 2 Nuevo"}
    resp2 = client.put(f"/products/{product_id}", json=upd, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "Prod 2 Nuevo"


def test_soft_delete_product(client: TestClient, db_session: Session):
    _, brand = seed_admin_and_brand(db_session)
    headers = login(client)
    payload = {
        "sku": "SKU-3",
        "name": "Prod 3",
        "description": "Desc3",
        "price": 30.00,
        "brand_id": brand.id,
        "status": True
    }
    resp = client.post("/products/", json=payload, headers=headers)
    assert resp.status_code == 200
    product_id = resp.json()["id"]
    resp_del = client.delete(f"/products/{product_id}", headers=headers)
    assert resp_del.status_code == 204
