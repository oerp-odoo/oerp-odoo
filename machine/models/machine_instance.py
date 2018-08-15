from odoo import models, fields


class MachineInstance(models.Model):
    """Machine instance to create specific environment used.

    It can be used as a template for other machine instances if
    template field is set to true, otherwise all parameters must be
    set manually.
    """

    _name = 'machine.instance'
    _description = 'Machine Instance'

    name = fields.Char(required=True)
    is_virtual = fields.Boolean(default=True)
    is_container = fields.Boolean()
    cpu_id = fields.Many2one('machine.cpu', "CPU")
    os_id = fields.Many2one('machine.os', "Operating System")
    os_user_ids = fields.One2many(
        'machine.instance.os_user', 'machine_instance_id', "OS Users")
    dbs_instance_ids = fields.One2many(
        'machine.dbs.instance',
        'machine_instance_id',
        "Database System Instances")
    amount_storage_capacity = fields.Float(
        "Storage Capacity (GB)")
    amount_ram = fields.Float("RAM (GB)")
    parent_id = fields.Many2one(
        'machine.instance',
        "Machine Template",
        domain=[('is_template', '=', True)])
    child_ids = fields.One2many(
        'machine.instance',
        'parent_id',
        "Machine Instances",
        domain=[('is_template', '=', False)])
    partner_id = fields.Many2one(
        'res.partner',
        "Partner",
        help="Partner that uses this machine instance.")
    ip = fields.Char("External IP")
    domain = fields.Char()
    # Template only fields.
    is_template = fields.Boolean("Is Template")
    fields_sync = fields.Boolean(
        "Fields Synchronization",
        help="If set, specified fields will be synced using template. In this"
        " mode, those fields can't be edited on instance.")


class MachineInstanceOsUser(models.Model):
    """Model to specify OS users on specific instance."""

    _name = 'machine.instance.os_user'
    _description = 'Machine Instance OS Users'

    name = fields.Char("Name and Surname")
    username = fields.Char("Username", required=True)
    machine_instance_id = fields.Many2one(
        'machine.instance', "Machine Instance", required=True,)
