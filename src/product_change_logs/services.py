from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.entities.product import Product
from src.entities.product_change_log import ProductChangeLog
from src.entities.action_status import ActionStatus
from src.entities.user import User
from . import models


def get_or_create_action(db: Session, name: str, description: str = "") -> ActionStatus:
    action = db.query(ActionStatus).filter(ActionStatus.name == name).first()
    if action:
        return action
    action = ActionStatus(name=name, description=description or name)
    db.add(action)
    db.commit(); db.refresh(action)
    return action


def log_product_change(db: Session, product_id: int, changed_by: int, action_name: str, field: str, old_value: str | None, new_value: str | None) -> ProductChangeLog:
    if not db.query(Product).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    if not db.query(User).filter(User.id == changed_by).first():
        raise HTTPException(status_code=404, detail="User not found")
    action = get_or_create_action(db, action_name, action_name)
    log = ProductChangeLog(
        product_id=product_id,
        changed_by=changed_by,
        action_id=action.id,
        field_changed=field,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(log)
    db.commit(); db.refresh(log)
    return log


def diff_and_log(db: Session, product: Product, data_before: Dict[str, Any], data_after: Dict[str, Any], user_id: int, action_name: str = "UPDATE"):
    for field, old_val in data_before.items():
        if field not in data_after:
            continue
        new_val = data_after[field]
        if old_val != new_val:
            log_product_change(db, product.id, user_id, action_name, field, str(old_val) if old_val is not None else None, str(new_val) if new_val is not None else None)


def list_logs_by_product(db: Session, product_id: int) -> List[ProductChangeLog]:
    return db.query(ProductChangeLog).filter(ProductChangeLog.product_id == product_id).order_by(ProductChangeLog.changed_at.desc()).all()


def list_all_logs(db: Session) -> List[ProductChangeLog]:
    return db.query(ProductChangeLog).order_by(ProductChangeLog.changed_at.desc()).all()


def enrich_with_actions(db: Session, logs: List[ProductChangeLog]) -> List[models.ProductChangeLogResponse]:
    action_ids = {l.action_id for l in logs}
    actions = db.query(ActionStatus).filter(ActionStatus.id.in_(action_ids)).all() if action_ids else []
    lookup = {a.id: a.name for a in actions}
    return [models.ProductChangeLogResponse(
        id=l.id,
        product_id=l.product_id,
        changed_by=l.changed_by,
        action_id=l.action_id,
        action_name=lookup.get(l.action_id),
        field_changed=l.field_changed,
        old_value=l.old_value,
        new_value=l.new_value,
        changed_at=str(l.changed_at)
    ) for l in logs]
