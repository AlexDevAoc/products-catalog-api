from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.auth.service import get_password_hash
from src.entities.user import User
from src.entities.role import Role
from src.entities.user_role import UserRole

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASS = "Admin123!"


def seed_admin(db: Session):
    # Role
    admin_role = db.query(Role).filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Admin role")
        db.add(admin_role); db.commit(); db.refresh(admin_role)
    # User
    admin_user = db.query(User).filter_by(email=ADMIN_EMAIL).first()
    if not admin_user:
        admin_user = User(
            email=ADMIN_EMAIL,
            first_name="Admin",
            last_name="User",
            password=get_password_hash(ADMIN_PASS)
        )
        db.add(admin_user); db.commit(); db.refresh(admin_user)
    # Link role
    user_role = db.query(UserRole).filter_by(user_id=admin_user.id, role_id=admin_role.id).first()
    if not user_role:
        db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id)); db.commit()
    return admin_user


def login(client: TestClient):
    resp = client.post("/auth/token", data={"username": ADMIN_EMAIL, "password": ADMIN_PASS})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_users_empty(client: TestClient, db_session: Session):
    seed_admin(db_session)
    headers = login(client)
    resp = client.get("/users/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # at least the admin


def test_update_user_first_name(client: TestClient, db_session: Session):
    admin = seed_admin(db_session)
    headers = login(client)
    payload = {"first_name": "NuevoNombre"}
    resp = client.put(f"/users/{admin.id}", json=payload, headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["first_name"] == "NuevoNombre"


def test_change_password(client: TestClient, db_session: Session):
    seed_admin(db_session)
    headers = login(client)
    payload = {"current_password": ADMIN_PASS, "new_password": "OtraPass123!", "new_password_confirm": "OtraPass123!"}
    resp = client.put("/users/change-password", json=payload, headers=headers)
    assert resp.status_code == 200, resp.text
