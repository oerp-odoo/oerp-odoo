from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

PRIORITY = [(1, 'Low'), (2, 'Normal'), (3, 'High')]
# Machine fields that can be synced.
SYNC_FIELDS = [
    'is_virtual',
    'is_container',
    'cpu_id',
    'os_id',
    'amount_ram',
    'amount_storage_capacity',
]


class MachineInstance(models.Model):
    """Machine instance to create specific environment used.

    It can be used as a template for other machine instances if
    template field is set to true, otherwise all parameters must be
    set manually.
    """

    _name = 'machine.instance'
    _inherit = 'mail.thread'
    _description = 'Machine Instance'

    name = fields.Char(required=True, track_visibility='onchange')
    is_virtual = fields.Boolean(default=True, track_visibility='onchange')
    is_container = fields.Boolean(track_visibility='onchange')
    cpu_id = fields.Many2one('machine.cpu', "CPU", track_visibility='onchange')
    os_id = fields.Many2one(
        'machine.os', "Operating System", track_visibility='onchange')
    os_user_ids = fields.One2many(
        'machine.instance.os_user', 'machine_instance_id', "OS Users")
    _os_users_count = fields.Integer("_os_users_count")
    os_users_count = fields.Integer(
        "OS Users Count",
        compute='_compute_os_users_count',
        inverse='_inverse_os_users_count',
        store=True)
    dbs_instance_ids = fields.One2many(
        'machine.dbs.instance',
        'machine_instance_id',
        "Database System Instances")
    change_log_ids = fields.One2many(
        'machine.instance.change_log', 'machine_instance_id', "Change Log")
    amount_storage_capacity = fields.Float(
        "Storage Capacity (GB)", track_visibility='onchange')
    amount_ram = fields.Float("RAM (GB)", track_visibility='onchange')
    parent_id = fields.Many2one(
        'machine.instance',
        "Machine Template",
        domain=[('is_template', '=', True)],
        track_visibility='onchange')
    child_ids = fields.One2many(
        'machine.instance',
        'parent_id',
        "Machine Instances",
        domain=[('is_template', '=', False)])
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one(
        'res.partner',
        "Partner",
        help="Partner that uses this machine instance.",
        track_visibility='onchange')
    partner_contact_id = fields.Many2one(
        'res.partner',
        "Contact",
        help="Contact which email will be used when communicating about "
        "machine.",
        track_visibility='onchange')
    user_id = fields.Many2one(
        'res.users', "Responsible", track_visibility='onchange')
    ip = fields.Char("External IP", track_visibility='onchange')
    domain = fields.Char(track_visibility='onchange')
    tag_ids = fields.Many2many('machine.tag', string="Tags")
    machine_group_ids = fields.Many2many(
        'machine.group',
        'machine_group_machine_instance_rel',
        'instance_id',
        'group_id',
        string="Machine Groups")
    # Fields used for template only.
    is_template = fields.Boolean("Is Template", track_visibility='onchange')
    sync = fields.Boolean(
        "Fields Synchronization",
        help="If set, specified fields will be synced using template.",
        track_visibility='onchange')

    @api.one
    @api.depends('os_user_ids', '_os_users_count')
    def _compute_os_users_count(self):
        os_users_count = len(self.os_user_ids) or self._os_users_count
        self.os_users_count = os_users_count

    @api.one
    def _inverse_os_users_count(self):
        self._os_users_count = self.os_users_count

    @api.one
    @api.constrains('is_template', 'sync', *SYNC_FIELDS)
    def _check_sync(self):
        if not self.is_template and self.sync:
            template = self.parent_id
            if any(self[fld] != template[fld] for fld in SYNC_FIELDS):
                raise ValidationError(
                    _("Synced fields values can't be modified on machine"
                        " instance, if syncing is enabled."))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            addr = self.partner_id.address_get(['contact'])
            self.partner_contact_id = (
                addr.get('contact') or self.partner_id.id)
        else:
            self.partner_contact_id = False

    def _filter_sync_values(self, vals):
        self.ensure_one()
        return {k: v for (k, v) in vals.items() if k in SYNC_FIELDS}

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

    # mail.thread specific.
    @api.multi
    def message_get_suggested_recipients(self):
        """Add suggested recipients for machine.instance model."""
        recipients = super(
            MachineInstance, self).message_get_suggested_recipients()
        for rec in self.filtered(lambda r: r.partner_contact_id):
            rec._message_add_suggested_recipient(
                recipients,
                partner=rec.partner_contact_id,
                reason=_("Partner Contact"))
        return recipients

    @api.multi
    def message_get_default_recipients(self):
        """Get default recipients using machine.instance model."""
        res = {}
        for rec in self:
            partner_contact_id = rec.partner_contact_id.id
            res[rec.id] = {
                'partner_ids': [
                    partner_contact_id] if partner_contact_id else [],
                'email_to': False,
                'email_cc': rec.user_id.partner_id.email
            }
        return res

    @api.multi
    def toggle_active(self):
        """Override to propagate change to template childs."""
        for record in self:
            super(MachineInstance, record).toggle_active()
            if record.is_template:
                record.with_context(active_test=False).child_ids.write(
                    {'active': record.active})


class MachineInstanceChangeLog(models.Model):
    """Model to specify changes that occurred for specific instance."""

    _name = 'machine.instance.change_log'
    _description = 'Machine Instance Change Log'
    _order = 'date'

    name = fields.Char(
        "Description", required=True, help="Change description")
    machine_instance_id = fields.Many2one(
        'machine.instance', "Machine Instance", required=True)
    date = fields.Datetime(
        required=True,
        help="When change happened or specify date it is being planned "
        "to be changed in advance")
    duration = fields.Float(required=True, default=1.0, help="In Hours")
    user_id = fields.Many2one('res.users', "Responsible")
    priority = fields.Selection(
        PRIORITY,
        default=2,
        required=True,
        help="How important is the change. "
        "Low can be treated as wishlist change\n. Normal as regularly planned"
        " change. High as emergency when something needs to be fixed fast.")

    # Helper methods for email template.
    def get_machine_name(self):
        """Retrieve machine name used for customer.

        We use this order: domain -> IP -> Machine Name.
        """
        self.ensure_one()
        machine = self.machine_instance_id
        return machine.domain or machine.ip or machine.name


class MachineInstanceOsUser(models.Model):
    """Model to specify OS users on specific instance."""

    _name = 'machine.instance.os_user'
    _description = 'Machine Instance OS Users'
    _rec_name = 'username'

    name = fields.Char("Name and Surname")
    username = fields.Char("Username", required=True)
    machine_instance_id = fields.Many2one(
        'machine.instance', "Machine Instance", required=True,)

    _sql_constraints = [(
        'username_uniq',
        'unique (username, machine_instance_id)',
        "Username already exists !",
    )]
