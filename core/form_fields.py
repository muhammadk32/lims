"""
Reception Form Field Catalog.

Defines every field the system CAN display on the reception/order page.
Each entry is (key, section, label, input_type, default_visible, default_required).

To add a new field to the system:
  1. Add it to FORM_FIELDS below
  2. Add handling in orders/routes.py POST handler
  3. It will automatically appear in the admin settings page

Field types:
  - text        single-line text input
  - textarea    multi-line text
  - tel         phone number
  - email       email
  - number      integer
  - decimal     float
  - age         special: value + unit (years/months/days)
  - select      dropdown (options passed separately)
  - checkbox    boolean
  - date        date picker
  - datetime    date + time picker
  - file        file upload
  - search      searchable combobox (tests, patients)
  - display     read-only info block
"""


# ============================================================
# SECTIONS
# ============================================================
# Ordered list of sections and their display labels.
# Order here determines the order sections appear in the form.

FORM_SECTIONS = [
    ('patient',   'Patient Information'),
    ('contact',   'Contact & Logistics'),
    ('referral',  'Referral & Scheduling'),
    ('tests',     'Tests & Panels'),
    ('billing',   'Billing'),
    ('output',    'Output Options'),
]


# ============================================================
# FIELD CATALOG
# ============================================================
# Each tuple: (key, section, label, input_type, default_visible, default_required)
#
# Defaults are used when seeding FormFieldConfig for the first time.
# After that, the DB is the source of truth.

FORM_FIELDS = [
    # ---------- Patient ----------
    ('patient_name',            'patient',  'Patient Name',          'text',     True,  True),
    ('patient_age',             'patient',  'Age',                   'age',      True,  True),
    ('patient_gender',          'patient',  'Gender',                'select',   True,  True),
    ('patient_phone',           'patient',  'Mobile No.',            'tel',      True,  False),
    ('patient_email',           'patient',  'Email',                 'email',    False, False),
    ('patient_cnic',            'patient',  'CNIC / National ID',    'text',     False, False),
    ('patient_mr_no',           'patient',  'M.R. No.',              'text',     False, False),
    ('patient_marital_status',  'patient',  'Marital Status',        'select',   False, False),
    ('patient_blood_group',     'patient',  'Blood Group',           'select',   False, False),
    ('patient_father_husband',  'patient',  'Father / Husband',      'text',     False, False),
    ('patient_address',         'patient',  'Address',               'textarea', False, False),
    ('patient_picture',         'patient',  'Picture',               'file',     False, False),
    ('patient_document_image',  'patient',  'Document Image',        'file',     False, False),

    # ---------- Contact & Logistics ----------
    ('branch',                  'contact',  'Branch',                'select',   False, False),
    ('center',                  'contact',  'Center',                'select',   False, False),
    ('sample_location',         'contact',  'Sample Location',       'select',   False, False),
    ('insurance',               'contact',  'Insurance',             'select',   False, False),
    ('home_sampling',           'contact',  'Home Sampling',         'checkbox', False, False),

    # ---------- Referral & Scheduling ----------
    ('sample_date',             'referral', 'Sample Date',           'datetime', True,  True),
    ('referred_by',             'referral', 'Referred by',           'select',   True,  False),
    ('reporting_date',          'referral', 'Reporting Date',        'date',     False, False),
    ('ipd_location',            'referral', 'IPD Location',          'text',     False, False),
    ('urgent',                  'referral', 'Urgent',                'checkbox', False, False),
    ('notes',                   'referral', 'Notes',                 'textarea', False, False),

    # ---------- Tests ----------
    ('test_search',             'tests',    'Test Search',           'search',   True,  True),
    ('test_reporting_date',     'tests',    'Reporting Date (per test)',   'date',   False, False),
    ('test_sample_required',    'tests',    'Sample Required (per test)',  'text',   False, False),
    ('test_sample_received',    'tests',    'Sample Received (per test)',  'select', False, False),
    ('test_comments',           'tests',    'Comments (per test)',         'text',   False, False),

    # ---------- Billing ----------
    ('discount_percent',        'billing',  'Discount %',            'decimal',  True,  False),
    ('discount_amount',         'billing',  'Discount Amount',       'decimal',  True,  False),
    ('discount_reason',         'billing',  'Discount Reason',       'text',     False, False),
    ('discounted_by',           'billing',  'Discounted By',         'text',     False, False),
    ('other_charges',           'billing',  'Other Charges',         'decimal',  False, False),
    ('company_bill',            'billing',  'Company Bill',          'checkbox', False, False),
    ('payment_amount',          'billing',  'Received Amount',       'decimal',  True,  False),
    ('payment_method',          'billing',  'Payment Mode',          'select',   True,  False),
    ('payment_reference',       'billing',  'Payment Reference',     'text',     False, False),

    # ---------- Output ----------
    ('print_patient_copy',      'output',   'Patient Copy',          'checkbox', True,  False),
    ('print_lab_copy',          'output',   'Lab Copy',              'checkbox', False, False),
    ('auto_print_on_save',      'output',   'Auto Print on Save',    'checkbox', False, False),
]


# ============================================================
# PRESET PROFILES
# ============================================================
# Each preset is a dict: { field_key: {visible, required} }
# Used by the "Apply Preset" button in settings.
# Fields not listed fall back to catalog defaults.

PRESETS = {
    'simple': {
        'label': 'Simple',
        'description': 'Minimum fields — fast reception entry for high-volume labs.',
        'fields': {
            'patient_name':   {'visible': True,  'required': True},
            'patient_age':    {'visible': True,  'required': True},
            'patient_gender': {'visible': True,  'required': True},
            'patient_phone':  {'visible': True,  'required': False},
            'test_search':    {'visible': True,  'required': True},
            'discount_amount':{'visible': True,  'required': False},
            'payment_amount': {'visible': True,  'required': False},
            'payment_method': {'visible': True,  'required': False},
            'print_patient_copy': {'visible': True, 'required': False},
        },
    },
    'standard': {
        'label': 'Standard',
        'description': 'Balanced field set — recommended for most labs.',
        'fields': {
            'patient_email':      {'visible': True, 'required': False},
            'patient_cnic':       {'visible': True, 'required': False},
            'patient_address':    {'visible': True, 'required': False},
            'sample_date':        {'visible': True, 'required': True},
            'referred_by':        {'visible': True, 'required': False},
            'sample_location':    {'visible': True, 'required': False},
            'discount_percent':   {'visible': True, 'required': False},
            'discount_amount':    {'visible': True, 'required': False},
            'discount_reason':    {'visible': True, 'required': False},
            'payment_amount':     {'visible': True, 'required': False},
            'payment_method':     {'visible': True, 'required': False},
            'print_patient_copy': {'visible': True, 'required': False},
        },
    },
    'detailed': {
        'label': 'Detailed',
        'description': 'Full-featured — for pathology labs, hospitals, and research.',
        'fields': {
            'patient_email':          {'visible': True, 'required': False},
            'patient_cnic':           {'visible': True, 'required': False},
            'patient_mr_no':          {'visible': True, 'required': False},
            'patient_marital_status': {'visible': True, 'required': False},
            'patient_blood_group':    {'visible': True, 'required': False},
            'patient_father_husband': {'visible': True, 'required': False},
            'patient_address':        {'visible': True, 'required': False},
            'branch':                 {'visible': True, 'required': False},
            'sample_location':        {'visible': True, 'required': False},
            'insurance':              {'visible': True, 'required': False},
            'home_sampling':          {'visible': True, 'required': False},
            'sample_date':            {'visible': True, 'required': True},
            'referred_by':            {'visible': True, 'required': False},
            'reporting_date':         {'visible': True, 'required': False},
            'urgent':                 {'visible': True, 'required': False},
            'notes':                  {'visible': True, 'required': False},
            'discount_percent':       {'visible': True, 'required': False},
            'discount_amount':        {'visible': True, 'required': False},
            'discount_reason':        {'visible': True, 'required': False},
            'discounted_by':          {'visible': True, 'required': False},
            'other_charges':          {'visible': True, 'required': False},
            'payment_amount':         {'visible': True, 'required': False},
            'payment_method':         {'visible': True, 'required': False},
            'payment_reference':      {'visible': True, 'required': False},
            'print_patient_copy':     {'visible': True, 'required': False},
            'print_lab_copy':         {'visible': True, 'required': False},
        },
    },
}


# ============================================================
# Helpers
# ============================================================
def get_default_profile():
    """Return the default preset name for a fresh install."""
    return 'simple'


def get_field_definitions():
    """Return the catalog as a dict keyed by field_key."""
    result = {}
    for (key, section, label, input_type, vis, req) in FORM_FIELDS:
        result[key] = {
            'key': key,
            'section': section,
            'label': label,
            'input_type': input_type,
            'default_visible': vis,
            'default_required': req,
        }
    return result


def get_section_label(section_key):
    for k, label in FORM_SECTIONS:
        if k == section_key:
            return label
    return section_key.title()


def get_fields_by_section():
    """Return {section_key: [fields...]} in catalog order."""
    out = {k: [] for k, _ in FORM_SECTIONS}
    for (key, section, label, input_type, vis, req) in FORM_FIELDS:
        out[section].append({
            'key': key,
            'label': label,
            'input_type': input_type,
            'default_visible': vis,
            'default_required': req,
        })
    return out