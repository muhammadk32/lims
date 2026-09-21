"""
Central audit logging helper.

Usage:
    from core.audit import log_action
    log_action('create', 'patient', patient.id, f'Created patient {patient.full_name}')
"""
import json
from flask import request, has_request_context
from flask_login import current_user
from extensions import db


def log_action(action: str, entity: str, entity_id=None, summary: str = '', extra: dict = None):
    """
    Write an audit log entry. Safe to call anywhere.
    Never raises — logging must not break the app.
    """
    try:
        from core.models import AuditLog

        user_id = None
        username = None
        if current_user and getattr(current_user, 'is_authenticated', False):
            user_id = current_user.id
            username = current_user.username

        ip = None
        ua = None
        if has_request_context():
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip and ',' in ip:
                ip = ip.split(',')[0].strip()
            ua = (request.user_agent.string or '')[:255] if request.user_agent else None

        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            entity=entity,
            entity_id=entity_id,
            summary=(summary or '')[:255],
            extra=json.dumps(extra) if extra else None,
            ip_address=ip,
            user_agent=ua,
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # Don't break app if audit fails
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f'[audit] failed: {e}')