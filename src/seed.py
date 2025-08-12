import os
import logging
from sqlalchemy.orm import Session
from .database.core import SessionLocal
from .auth.service import get_password_hash
from .entities.user import User
from .entities.role import Role
from .entities.user_role import UserRole
from .entities.permission import Permission
from .entities.role_permission import RolePermission

ADMIN_ROLE_NAME = "admin"
ANON_ROLE_NAME = "anonymous"
FULL_ACCESS_PERMISSION = "FULL_ACCESS"
READ_PRODUCTS_PERMISSION = "READ_PRODUCTS"
ADMIN_USER_EMAIL = os.getenv("ADMIN_USER_EMAIL")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")
ANON_EMAIL = os.getenv("ANON_EMAIL")
ANON_FIRST_NAME = "Anon"
ANON_LAST_NAME = "User"
ANON_PASSWORD = os.getenv("ANON_PASSWORD")

ADMIN_USERS = [
    {"email": ADMIN_USER_EMAIL, "first_name": "Admin", "last_name": "One", "password": DEFAULT_ADMIN_PASSWORD},
]


def seed():
    run_seed = os.getenv("RUN_SEED", "false").lower() == "true"
    if not run_seed:
        logging.info("Seeding skipped (set RUN_SEED=true to enable).")
        return
    logging.info("Starting seed process...")
    db: Session = SessionLocal()
    try:
        # Roles
        admin_role = db.query(Role).filter(Role.name == ADMIN_ROLE_NAME).first()
        if not admin_role:
            admin_role = Role(name=ADMIN_ROLE_NAME, description="Administrator with full access")
            db.add(admin_role)
            db.commit(); db.refresh(admin_role)
            logging.info("Created role 'admin'")
        anon_role = db.query(Role).filter(Role.name == ANON_ROLE_NAME).first()
        if not anon_role:
            anon_role = Role(name=ANON_ROLE_NAME, description="Anonymous read-only role")
            db.add(anon_role)
            db.commit(); db.refresh(anon_role)
            logging.info("Created role 'anonymous'")

        # Permissions
        full_access = db.query(Permission).filter(Permission.name == FULL_ACCESS_PERMISSION).first()
        if not full_access:
            full_access = Permission(name=FULL_ACCESS_PERMISSION, description="Access to all endpoints")
            db.add(full_access)
            db.commit(); db.refresh(full_access)
            logging.info("Created permission FULL_ACCESS")
        read_products = db.query(Permission).filter(Permission.name == READ_PRODUCTS_PERMISSION).first()
        if not read_products:
            read_products = Permission(name=READ_PRODUCTS_PERMISSION, description="Read products only")
            db.add(read_products)
            db.commit(); db.refresh(read_products)
            logging.info("Created permission READ_PRODUCTS")

        # Assign permissions to roles (idempotent)
        def ensure_role_perm(r: Role, p: Permission):
            exists = db.query(RolePermission).filter(RolePermission.role_id == r.id, RolePermission.permission_id == p.id).first()
            if not exists:
                db.add(RolePermission(role_id=r.id, permission_id=p.id))
                db.commit()
        ensure_role_perm(admin_role, full_access)
        ensure_role_perm(anon_role, read_products)

        # Admin users
        for u in ADMIN_USERS:
            user = db.query(User).filter(User.email == u["email"]).first()
            if not user:
                user = User(
                    email=u["email"],
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    password=get_password_hash(u["password"])
                )
                db.add(user)
                db.commit(); db.refresh(user)
                logging.info(f"Created admin user {u['email']}")
            # Assign role
            user_role = db.query(UserRole).filter(UserRole.user_id == user.id).first()
            if not user_role:
                db.add(UserRole(user_id=user.id, role_id=admin_role.id))
                db.commit()
        # Anonymous user (single shared)
        anon_user = db.query(User).filter(User.email == ANON_EMAIL).first()
        if not anon_user:
            anon_user = User(
                email=ANON_EMAIL,
                first_name=ANON_FIRST_NAME,
                last_name=ANON_LAST_NAME,
                password=get_password_hash(ANON_PASSWORD)
            )
            db.add(anon_user)
            db.commit(); db.refresh(anon_user)
            logging.info("Created anonymous user")
        anon_user_role = db.query(UserRole).filter(UserRole.user_id == anon_user.id).first()
        if not anon_user_role:
            db.add(UserRole(user_id=anon_user.id, role_id=anon_role.id))
            db.commit()
        logging.info("Seed process completed.")
    except Exception as e:
        logging.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()
