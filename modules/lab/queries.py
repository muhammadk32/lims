"""Query helpers for the lab verification workflow.

Pure data-fetching — no HTTP concerns, no flashing, no commits.
"""
from datetime import datetime, date, timedelta

from sqlalchemy import or_

from extensions import db
from modules.orders.models import Order, OrderItem, OrderStatus
from modules.patients.models import Patient


def parse_date(value, fallback):
    """Parse YYYY-MM-DD or return fallback."""
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return fallback


def default_date_range():
    """Return (date_from, date_to) defaults: last 7 days."""
    today = date.today()
    return today - timedelta(days=7), today


def get_verify_queue_items(q, date_from, date_to):
    """Return list of OrderItem candidates: top-level, non-cancelled,
    within date range, matching optional search, not yet verified."""
    query = (
        OrderItem.query
        .join(Order, OrderItem.order_id == Order.id)
        .filter(OrderItem.parent_item_id.is_(None))
        .filter(Order.status != OrderStatus.CANCELLED)
        .filter(db.func.date(Order.created_at).between(date_from, date_to))
    )

    if q:
        like = f'%{q}%'
        query = (
            query
            .join(Patient, Order.patient_id == Patient.id)
            .filter(or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
            ))
        )

    candidates = query.order_by(OrderItem.id.desc()).all()
    return [i for i in candidates if i.is_verifiable and not i.is_verified]


def group_by_order(items):
    """Return distinct parent orders, preserving newest-first order."""
    seen, orders = set(), []
    for item in items:
        if item.order.id not in seen:
            seen.add(item.order.id)
            orders.append(item.order)
    return orders


def load_items_for_action(item_ids, require_ready):
    """Return (valid_items, skipped_count).

    require_ready=True  → only items that are verifiable AND not verified
    require_ready=False → items that are verifiable OR already verified
    """
    valid, skipped = [], 0
    for iid in item_ids:
        item = OrderItem.query.get(iid)
        if not item or item.is_child:
            skipped += 1
            continue

        if require_ready:
            if not item.is_verifiable or item.is_verified:
                skipped += 1
                continue
        else:
            if not (item.is_verifiable or item.is_verified):
                skipped += 1
                continue

        valid.append(item)
    return valid, skipped