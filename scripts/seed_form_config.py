"""
Seed the reception form configuration.

Run once on first install (or when adding new fields to the catalog).
Safe to run multiple times — only inserts missing fields.

Usage:
    python -m scripts.seed_form_config
    python -m scripts.seed_form_config --reset   # wipe and re-seed
"""
import argparse
import sys

from app import create_app
from extensions import db
from core.models import FormFieldConfig, FormSectionConfig
from core.form_fields import (
    FORM_FIELDS, FORM_SECTIONS, PRESETS, get_default_profile,
)


def seed(reset=False):
    app = create_app()
    with app.app_context():

        if reset:
            print('⚠️  Wiping existing form configs...')
            FormFieldConfig.query.delete()
            FormSectionConfig.query.delete()
            db.session.commit()

        # ---------- Sections ----------
        print('→ Seeding sections...')
        existing_sections = {s.section_key for s in FormSectionConfig.query.all()}
        added_sections = 0
        for i, (key, _label) in enumerate(FORM_SECTIONS):
            if key in existing_sections:
                continue
            db.session.add(FormSectionConfig(
                section_key=key,
                is_visible=True,
                sort_order=i,
            ))
            added_sections += 1
        db.session.commit()
        print(f'  ✓ {added_sections} sections added')

        # ---------- Fields (from default profile) ----------
        print('→ Seeding fields...')
        default_profile = get_default_profile()
        preset = PRESETS.get(default_profile, {'fields': {}})
        preset_overrides = preset.get('fields', {})

        existing_fields = {f.field_key for f in FormFieldConfig.query.all()}
        added_fields = 0

        for i, (key, section, label, input_type, default_vis, default_req) in enumerate(FORM_FIELDS):
            if key in existing_fields:
                continue

            override = preset_overrides.get(key, {})
            vis = override.get('visible', default_vis)
            req = override.get('required', default_req)

            if req:
                vis = True

            db.session.add(FormFieldConfig(
                field_key=key,
                section=section,
                is_visible=vis,
                is_required=req,
                default_value=None,
                custom_label=None,
                sort_order=i,
            ))
            added_fields += 1

        db.session.commit()
        print(f'  ✓ {added_fields} fields added')

        # ---------- Summary ----------
        total_fields = FormFieldConfig.query.count()
        visible_fields = FormFieldConfig.query.filter_by(is_visible=True).count()
        required_fields = FormFieldConfig.query.filter_by(is_required=True).count()

        print()
        print('=' * 50)
        print('  FORM CONFIG SEEDED')
        print('=' * 50)
        print(f'  Total fields in catalog:   {len(FORM_FIELDS)}')
        print(f'  Fields in DB:              {total_fields}')
        print(f'  Visible:                   {visible_fields}')
        print(f'  Required:                  {required_fields}')
        print()
        print('  Default profile:', default_profile)
        print()
        print('  Next steps:')
        print('   1. Visit:  /settings/reception-form')
        print('=' * 50)


def main():
    parser = argparse.ArgumentParser(description='Seed reception form config.')
    parser.add_argument('--reset', action='store_true',
                        help='Wipe existing configs and re-seed')
    args = parser.parse_args()
    seed(reset=args.reset)


if __name__ == '__main__':
    main()