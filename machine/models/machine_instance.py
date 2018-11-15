from odoo import models, fields, api


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
    tag_ids = fields.Many2many('machine.tag', string="Tags")
    # Fields used for template only.
    is_template = fields.Boolean("Is Template")
    sync = fields.Boolean(
        "Fields Synchronization",
        help="If set, specified fields will be synced using template.\nIn this"
        " mode, those fields can't be edited on instance.")
    related_sync = fields.Boolean(
        "Fields Synchronization on Template",
        related='parent_id.sync',
        help="Technical field: used to check if sync option\nis enabled on "
        "template from machine instance.")

    @api.model
    def get_sync_fields(self):
        """Return machine fields that can be synced.

        Can be extended to include new fields to sync.

        Synchronization happens by propagating fields values from
        template to its instances if template and instances have
        syncing enabled.
        """
        return [
            'is_virtual',
            'is_container',
            'cpu_id',
            'os_id',
            'amount_ram',
            'amount_storage_capacity',
        ]

    def _filter_sync_values(self, vals):
        self.ensure_one()
        sync_fields = self.get_sync_fields()
        return {k: v for (k, v) in vals.items() if k in sync_fields}

    def _get_sync_instances(self):
        """Return instances that can be synchronized with templates."""
        templates = self.filtered(lambda r: r.sync)
        return templates.mapped('child_ids').filtered(lambda r: r.sync)

    def do_sync(self, vals):
        """Synchronize template with instances.

        vals here is expected to be coming from `write` method.
        """
        sync_instances = self._get_sync_instances()
        if sync_instances:
            vals_to_sync = self._filter_sync_values(vals)
            sync_instances.write(vals_to_sync)

    @api.multi
    def write(self, vals):
        """Extend to sync common fields with template and instances."""
        res = super(MachineInstance, self).write(vals)
        self.do_sync(vals)
        return res


class MachineInstanceOsUser(models.Model):
    """Model to specify OS users on specific instance."""

    _name = 'machine.instance.os_user'
    _description = 'Machine Instance OS Users'
    _rec_name = 'username'

    name = fields.Char("Name and Surname")
    username = fields.Char("Username", required=True)
    machine_instance_id = fields.Many2one(
        'machine.instance', "Machine Instance", required=True,)

    _sql_constraints = [
        ('username_uniq', 'unique (username)', "Username already exists !"),
    ]
