import ipaddress

import validators

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

PRIORITY = [('1', 'Low'), ('2', 'Normal'), ('3', 'High')]


class MachineInstance(models.Model):
    """Machine instance to create specific environment used.

    It can be used as a template for other machine instances if
    template field is set to true, otherwise all parameters must be
    set manually.
    """

    _name = 'machine.instance'
    _inherit = 'mail.thread'
    _description = 'Machine Instance'

    name = fields.Char(required=True, tracking=10)
    is_virtual = fields.Boolean(default=True, tracking=10)
    is_container = fields.Boolean(tracking=10)
    cpu_id = fields.Many2one('machine.cpu', "CPU", tracking=10)
    dbs_id = fields.Many2one('machine.dbs', "Database System", tracking=10)
    os_id = fields.Many2one(
        'machine.os',
        "Operating System",
        tracking=10,
    )
    change_log_ids = fields.One2many(
        'machine.instance.change_log',
        'machine_instance_id',
        "Change Log",
    )
    amount_storage_capacity = fields.Float(
        "Storage Capacity (GB)",
        tracking=10,
    )
    amount_ram = fields.Float("RAM (GB)", tracking=10)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one(
        'res.partner',
        "Partner",
        help="Partner that uses this machine instance.",
        tracking=10,
        copy=False,
    )
    company_identifier = fields.Integer(
        compute='_compute_company_identifier',
        store=True,
    )

    partner_contact_id = fields.Many2one(
        'res.partner',
        "Contact",
        help="Contact which email will be used when communicating about " "machine.",
        tracking=10,
        copy=False,
    )
    user_id = fields.Many2one('res.users', "Responsible", tracking=10)
    ip = fields.Char("External IP", tracking=10, copy=False)
    domain = fields.Char(tracking=10, copy=False)
    http_protocol = fields.Selection(
        [('http', "HTTP"), ('https', 'HTTPS')],
        copy=False,
        string="HTTP Protocol",
    )
    url = fields.Char(string="URL", compute='_compute_url')
    tag_ids = fields.Many2many('machine.tag', string="Tags")
    machine_group_ids = fields.Many2many(
        'machine.group',
        'machine_group_machine_instance_rel',
        'instance_id',
        'group_id',
        string="Machine Groups",
    )

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, company_identifier)',
            "The name must be unique globally or per company !",
        )
    ]

    @api.depends('partner_id.company_id')
    def _compute_company_identifier(self):
        for rec in self:
            rec.company_identifier = rec.partner_id.company_id.id or 0

    @api.depends('domain', 'http_protocol')
    def _compute_url(self):
        for rec in self:
            url = False
            if rec.domain and rec.http_protocol:
                url = f'{rec.http_protocol}://{rec.domain}'
            rec.url = url

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # Calling directly on childs, because company partner can
            # be of contact type and then childs would ignored.
            addr = self.partner_id.child_ids.address_get(adr_pref=['contact'])
            self.partner_contact_id = addr.get('contact') or self.partner_id.id
        else:
            self.partner_contact_id = False

    @api.constrains('ip')
    def _check_ip(self):
        for rec in self.filtered('ip'):
            try:
                ipaddress.ip_address(rec.ip)
            except ValueError as e:
                raise ValidationError(str(e))

    @api.constrains('domain')
    def _check_domain(self):
        for rec in self.filtered('domain'):
            domain = rec.domain
            is_valid = validators.domain(domain)
            if not is_valid:
                raise ValidationError(_("'%s' is not valid domain", domain))

    # mail.thread specific.
    def message_get_suggested_recipients(self):
        """Add suggested recipients for machine.instance model."""
        recipients = super().message_get_suggested_recipients()
        for rec in self.filtered(lambda r: r.partner_contact_id):
            rec._message_add_suggested_recipient(
                recipients, partner=rec.partner_contact_id, reason=_("Partner Contact")
            )
        return recipients

    def message_get_default_recipients(self):
        """Get default recipients using machine.instance model."""
        res = {}
        for rec in self:
            partner_contact_id = rec.partner_contact_id.id
            res[rec.id] = {
                'partner_ids': [partner_contact_id] if partner_contact_id else [],
                'email_to': False,
                'email_cc': rec.user_id.partner_id.email,
            }
        return res

    def generate_machine_name(self):
        """Retrieve machine name used for customer."""
        self.ensure_one()
        hostname = self.domain or self.ip
        name = self.name
        if hostname:
            # Lets not show main name if its already part of hostname.
            if name in hostname:
                name = hostname
            else:
                name = f'[{name}] {hostname}'
        return name

    @api.depends('name', 'domain', 'ip')
    def name_get(self):
        """Override to generate custom machine display name."""
        return [(r.id, r.generate_machine_name()) for r in self]

    def copy_data(self, default=None):
        """Extend to update name default value."""
        vals_list = super().copy_data(default=default)
        for vals in vals_list:
            if 'name' in vals:
                name = vals['name']
                vals['name'] = f'{name}-copy'
        return vals_list


class MachineInstanceChangeLog(models.Model):
    """Model to specify changes that occurred for specific instance."""

    _name = 'machine.instance.change_log'
    _description = 'Machine Change Log'
    _order = 'date'

    name = fields.Char("Description", required=True, help="Change description")
    machine_instance_id = fields.Many2one(
        'machine.instance',
        "Machine",
        required=True,
        ondelete='restrict',
    )
    machine_name = fields.Char(
        string="Machine Display Name",
        related='machine_instance_id.display_name',
    )
    date = fields.Datetime(
        required=True,
        help="When change happened or specify date it is being planned "
        "to be changed in advance",
    )
    duration = fields.Float(required=True, default=1.0, help="In Hours")
    user_id = fields.Many2one('res.users', "Responsible")
    priority = fields.Selection(
        PRIORITY,
        default='2',
        required=True,
        help="How important is the change. "
        "Low can be treated as wishlist change\n. Normal as regularly planned"
        " change. High as emergency when something needs to be fixed fast.",
    )
