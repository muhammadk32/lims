"""
Central place for role definitions and permission checks.
Import: from core.roles import Role, has_permission
"""

class Role:
    ADMIN         = 'admin'
    DOCTOR        = 'doctor'
    TECHNICIAN    = 'technician'
    RECEPTIONIST  = 'receptionist'

    CHOICES = [ADMIN, DOCTOR, TECHNICIAN, RECEPTIONIST]

    LABELS = {
        ADMIN:        'Administrator',
        DOCTOR:       'Doctor',
        TECHNICIAN:   'Lab Technician',
        RECEPTIONIST: 'Receptionist',
    }


# ---------- Permission matrix ----------
# Define each named capability and which roles have it.
PERMISSIONS = {
    # User management
    'manage_users':           {Role.ADMIN},

    # Patients
    'view_patients':          {Role.ADMIN, Role.DOCTOR, Role.TECHNICIAN, Role.RECEPTIONIST},
    'create_patient':         {Role.ADMIN, Role.RECEPTIONIST},
    'edit_patient':           {Role.ADMIN, Role.RECEPTIONIST},
    'delete_patient':         {Role.ADMIN},

    # Tests (catalog)
    'view_tests':             {Role.ADMIN, Role.DOCTOR, Role.TECHNICIAN, Role.RECEPTIONIST},
    'manage_tests':           {Role.ADMIN},   # create/edit/archive

    # Tests (settings — formats, categories, units, panels, bulk)
    'manage_test_settings':   {Role.ADMIN},   # ← NEW

    # Orders
    'view_orders':            {Role.ADMIN, Role.DOCTOR, Role.TECHNICIAN, Role.RECEPTIONIST},
    'create_order':           {Role.ADMIN, Role.DOCTOR, Role.RECEPTIONIST},
    'update_order_status':    {Role.ADMIN, Role.TECHNICIAN},
    'cancel_order':           {Role.ADMIN},

    # Results
    'view_results':           {Role.ADMIN, Role.DOCTOR, Role.TECHNICIAN},
    'enter_results':          {Role.ADMIN, Role.TECHNICIAN},

    # Reports
    'view_reports':           {Role.ADMIN, Role.DOCTOR, Role.TECHNICIAN, Role.RECEPTIONIST},

    # Billing
    'view_billing':           {Role.ADMIN, Role.RECEPTIONIST},
    'record_payment':         {Role.ADMIN, Role.RECEPTIONIST},
    'delete_payment':         {Role.ADMIN},
    'view_revenue_reports':   {Role.ADMIN},
}


def has_permission(role: str, permission: str) -> bool:
    """Return True if role is allowed the permission."""
    if not role or not permission:
        return False
    allowed = PERMISSIONS.get(permission, set())
    return role in allowed