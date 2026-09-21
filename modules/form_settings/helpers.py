"""
Helpers for the Reception Form config system.

These functions are the API that the reception/order page uses
to know which fields to show and how.
"""
from core.models import FormFieldConfig, FormSectionConfig
from core.form_fields import (
    FORM_SECTIONS, get_field_definitions, get_section_label,
)


def get_form_config():
    """
    Return a dict describing the current reception form configuration.

    Example structure:
    {
      'sections': [
        {'key': 'patient', 'label': 'Patient Information', 'is_visible': True, 'fields': [...]},
        {'key': 'contact', 'label': 'Contact & Logistics', 'is_visible': False, 'fields': [...]},
        ...
      ],
      'field_map': { 'patient_name': {...}, 'patient_phone': {...}, ... },
      'visible_fields': {'patient_name', 'patient_phone', ...},
      'required_fields': {'patient_name', 'patient_age', ...},
      'currency_symbol': 'Rs',
    }
    """
    definitions = get_field_definitions()
    field_configs = {c.field_key: c for c in FormFieldConfig.query.all()}
    section_configs = {c.section_key: c for c in FormSectionConfig.query.all()}

    sections_out = []
    field_map = {}
    visible_fields = set()
    required_fields = set()

    for section_key, section_label in FORM_SECTIONS:
        sec_cfg = section_configs.get(section_key)
        sec_visible = sec_cfg.is_visible if sec_cfg else True

        fields_in_section = []
        for key, defn in definitions.items():
            if defn['section'] != section_key:
                continue

            cfg = field_configs.get(key)
            is_visible = cfg.is_visible if cfg else defn['default_visible']
            is_required = cfg.is_required if cfg else defn['default_required']
            custom_label = cfg.custom_label if cfg else None
            default_value = cfg.default_value if cfg else None

            if is_required:
                is_visible = True

            field_info = {
                'key': key,
                'section': section_key,
                'label': custom_label or defn['label'],
                'original_label': defn['label'],
                'input_type': defn['input_type'],
                'is_visible': is_visible,
                'is_required': is_required,
                'default_value': default_value,
            }
            field_map[key] = field_info

            if is_visible:
                visible_fields.add(key)
                fields_in_section.append(field_info)
            if is_required:
                required_fields.add(key)

        sections_out.append({
            'key': section_key,
            'label': section_label,
            'is_visible': sec_visible,
            'fields': fields_in_section,
        })

    # Currency symbol from LabSettings
    from core.models import LabSettings
    ls = LabSettings.get()
    currency_symbol = ls.currency_symbol if ls else 'Rs'

    return {
        'sections': sections_out,
        'field_map': field_map,
        'visible_fields': visible_fields,
        'required_fields': required_fields,
        'currency_symbol': currency_symbol,
    }