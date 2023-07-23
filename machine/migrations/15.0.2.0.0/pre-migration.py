from odoo import SUPERUSER_ID, api

MODULE = 'machine'

XMLIDS_TO_REMOVE = [
    f'{MODULE}.machine_instance_template_menu',
    f'{MODULE}.machine_instance_menu',
    f'{MODULE}.machine_instance_action_form',
    f'{MODULE}.machine_instance_action_tree',
    f'{MODULE}.machine_instance_action',
    f'{MODULE}.machine_instance_view_form',
    f'{MODULE}.machine_instance_view_tree',
    f'{MODULE}.machine_instance_template_action_form',
    f'{MODULE}.machine_instance_template_action_tree',
    f'{MODULE}.machine_instance_template_action',
    f'{MODULE}.machine_instance_template_view_form',
    f'{MODULE}.machine_instance_template_view_tree',
    f'{MODULE}.machine_instance_common_view_form',
    f'{MODULE}.mail_template_planned_machine_change',
]

MODELS_TO_REMOVE = [
    'machine.dbs.instance',
    'machine.dbs.instance.database',
    'machine.instance.os_user',
]


def _remove_recs_by_xmlid(env, xmlids):
    for xmlid in xmlids:
        rec = env.ref(xmlid)
        rec.unlink()


def _remove_machine_templates(cr):
    cr.execute("SELECT id from machine_instance WHERE is_template = true")
    ids = [r[0] for r in cr.fetchall()]
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE
            module = 'machine' AND
            model = 'machine.instance' AND
            res_id IN %s

        """,
        (tuple(ids),),
    )
    cr.execute("""DELETE FROM machine_instance WHERE is_template = true""")


def _remove_models_data(cr, model_names, module):
    model_names = tuple(model_names)
    ext_names = [f'model_{m.replace(".", "_")}' for m in model_names]
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE
            module = %s AND
            name IN %s
        """,
        (module, tuple(ext_names)),
    )
    cr.execute("DELETE FROM ir_model WHERE model in %s", (model_names,))


def migrate(cr, version):
    """Pre migrate machine.

    Remove refactored/not existing views/actions.
    Remove machine.instance records that were of template type.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_recs_by_xmlid(env, XMLIDS_TO_REMOVE)
    _remove_machine_templates(cr)
    # Clean up wizard tables.
    cr.execute("DELETE FROM machine_email_recipient")
    cr.execute("DELETE FROM machine_email")
    _remove_models_data(cr, MODELS_TO_REMOVE, MODULE)
