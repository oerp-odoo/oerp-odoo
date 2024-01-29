from collections import defaultdict

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    label_recs_map = {}
    groups = defaultdict(lambda: env['stamp.material'])
    SML = env['stamp.material.label']
    for material in env['stamp.material'].search([]):
        label = material.label
        label_rec = label_recs_map.get(label)
        if not label_rec:
            label_rec = SML.create({'name': label})
            label_recs_map[label] = label_rec
        groups[label_rec] |= material
    for label_rec, materials in groups.items():
        materials.write({'label_id': label_rec.id})
