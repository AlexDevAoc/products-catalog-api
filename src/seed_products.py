import logging, os
from sqlalchemy.orm import Session
from .database.core import SessionLocal
from .entities.product import Product
from .entities.brand import Brand
from .entities.user import User
from .entities.role import Role
from .entities.user_role import UserRole

# DEFAULT_CREATOR_EMAIL = os.getenv("SEED_PRODUCTS_CREATOR")

PRODUCTS_BATCH = [
    {"sku": "PILLOW-AIR-1", "name": "Almohada AirFlow", "description": "Ventilación avanzada", "price": 28.90, "brand": "DreamRest"},
    {"sku": "PILLOW-GEL-1", "name": "Almohada Gel Fresh", "description": "Capa gel refrescante", "price": 34.50, "brand": "ComfortPlus"},
    {"sku": "MATTRESS-ORT-1", "name": "Colchón Ortopédico", "description": "Alta firmeza", "price": 640.00, "brand": "DreamRest"},
    {"sku": "MATTRESS-LUX-1", "name": "Colchón Lujo Plus", "description": "Capas premium", "price": 820.00, "brand": "ComfortPlus"},
    {"sku": "MATTRESS-BASIC-1", "name": "Colchón Básico", "description": "Opción económica", "price": 320.00, "brand": "EcoHome"},
    {"sku": "SOFA-CORN-1", "name": "Sofá Esquinero", "description": "Tela antimanchas", "price": 980.00, "brand": "UrbanLiving"},
    {"sku": "SOFA-CLASSIC-1", "name": "Sofá Clásico 3P", "description": "Confort estándar", "price": 650.00, "brand": "RelaxLine"},
    {"sku": "TABLE-COFFEE-1", "name": "Mesa de Centro Minimal", "description": "Madera y metal", "price": 180.00, "brand": "EcoHome"},
    {"sku": "CHAIR-DINE-1", "name": "Silla Comedor Madera", "description": "Acabado natural", "price": 95.50, "brand": "UrbanLiving"},
    {"sku": "CABINET-KITCH-1", "name": "Alacena Cocina Compacta", "description": "Puertas suaves", "price": 260.00, "brand": "RelaxLine"},
]

BRAND_FALLBACKS = ["DreamRest", "ComfortPlus", "EcoHome", "UrbanLiving", "RelaxLine"]

def seed_products():
    if os.getenv("RUN_SEED_PRODUCTS", "false").lower() != "true":
        logging.info("Product seeding skipped (set RUN_SEED_PRODUCTS=true to enable).")
        return
    logging.info("Starting product batch seeding...")
    db: Session = SessionLocal()
    try:
        admin_user_ids = _fetch_creators(db)
        if not admin_user_ids:
            logging.warning("No admin users found; aborting product seed.")
            return
        brand_cache = _ensure_brands(db)
        new_count = _insert_products(db, admin_user_ids, brand_cache)
        if new_count:
            db.commit()
        logging.info(f"Inserted {new_count} new products (batch)")
    except Exception as e:
        logging.error(f"Product seeding failed: {e}")
        db.rollback()
    finally:
        db.close()


def _fetch_creators(db: Session):
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    admin_user_ids: list[int] = []
    if admin_role:
        admin_user_ids = [row.user_id for row in db.query(UserRole).filter(UserRole.role_id == admin_role.id).all()]
    return admin_user_ids


def _ensure_brands(db: Session):
    brand_cache = {b.name: b.id for b in db.query(Brand).all()}
    for bname in BRAND_FALLBACKS:
        if bname not in brand_cache:
            b = Brand(name=bname, description=f"Brand {bname}")
            db.add(b); db.commit(); db.refresh(b)
            brand_cache[bname] = b.id
            logging.info(f"Created brand {bname}")
    return brand_cache


def _insert_products(db: Session, admin_user_ids: list[int], brand_cache: dict):
    existing_skus = {p[0] for p in db.query(Product.sku).all()}
    new_count = 0
    idx = 0
    for item in PRODUCTS_BATCH:
        if item["sku"] in existing_skus:
            continue
        brand_id = brand_cache.get(item["brand"]) or next(iter(brand_cache.values()))
        if admin_user_ids:
            creator_id = admin_user_ids[idx % len(admin_user_ids)]
            idx += 1
        product = Product(
            sku=item["sku"],
            name=item["name"],
            description=item["description"],
            price=item["price"],
            brand_id=brand_id,
            status=True,
            created_by=creator_id
        )
        db.add(product)
        new_count += 1
    return new_count
