from flask import render_template, request
from flask_login import login_required
from core.models import AuditLog
from core.decorators import admin_required
from extensions import db
from . import audit_bp


@audit_bp.route('/')
@login_required
@admin_required
def index():
    q = request.args.get('q', '').strip()
    action = request.args.get('action', '').strip()
    entity = request.args.get('entity', '').strip()
    page = request.args.get('page', 1, type=int)

    query = AuditLog.query

    if q:
        like = f'%{q}%'
        query = query.filter(
            (AuditLog.username.ilike(like)) |
            (AuditLog.summary.ilike(like))
        )
    if action:
        query = query.filter(AuditLog.action == action)
    if entity:
        query = query.filter(AuditLog.entity == entity)

    logs = query.order_by(AuditLog.id.desc()).paginate(page=page, per_page=30, error_out=False)

    # For filter dropdowns
    actions = [r[0] for r in db.session.query(AuditLog.action).distinct().all()]
    entities = [r[0] for r in db.session.query(AuditLog.entity).distinct().all()]

    return render_template(
        'audit/list.html',
        logs=logs,
        q=q,
        action=action,
        entity=entity,
        actions=sorted(actions),
        entities=sorted(entities),
    )