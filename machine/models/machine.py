from odoo import models, fields, _


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
    amount_storage_capacity = fields.Float(
        "Storage Capacity (GB)")
    amount_ram = fields.Float("RAM (GB)")
    template_id = fields.Many2one(
        'machine.instance',
        "Machine Template",
        domain=[('is_template', '=', True)])
    partner_id = fields.Many2one(
        'res.partner',
        "Partner",
        help="Partner that uses this machine instance.")
    ip = fields.Char("External IP")
    domain = fields.Char()
    os_instance_id = fields.Many2one(
        'machine.os.instance', "OS Instance")
    # Template only fields.
    is_template = fields.Boolean("Is Template")
    fields_sync = fields.Boolean(
        "Fields Synchronization",
        help="If set, specified fields will be synced using template. In this"
        " mode, those fields can't be edited on instance.")


class MachineCpuVendor(models.Model):
    """Model to show CPU vendors."""

    _name = 'machine.cpu.vendor'
    _description = 'Machine CPU Vendor'

    name = fields.Char(required=True, index=True)


class MachineCpuBrand(models.Model):
    """Model to show CPU brands."""

    _name = 'machine.cpu.brand'
    _description = 'Machine CPU Brand'

    name = fields.Char(required=True,)
    cpu_vendor_id = fields.Many2one(
        'machine.cpu.vendor', "CPU Vendor", required=True)


class MachineCpu(models.Model):
    """Model representing CPUs."""

    _name = 'machine.cpu'
    _description = 'Machine CPU'

    name = fields.Char(required=True,)
    cpu_brand_id = fields.Many2one(
        'machine.cpu.brand', "CPU Brand", required=True)
    cores = fields.Integer(required=True, default=2)
    clockspeed = fields.Float("Clockspeed in GHz", required=True)


class MachineDbInstance(models.Model):
    """Model representing database management system instance.

    You can specify databases, users and other details on that instance.
    """

    _name = 'machine.db.instance'
    _description = "Machine Database Instance"

    name = fields.Char(required=True,)
    db_id = fields.Many2one('machine.db', "Database System", required=True)
    port = fields.Integer(required=True,)
    # TODO: add possibility to specify users and databases.
    amount_users = fields.Integer("Users Count")
    amount_databases = fields.Integer("Databases Count")


class MachineDb(models.Model):
    """Model representing specific database system version."""

    _name = 'machine.db'
    _description = 'Machine Database'

    name = fields.Char("Version", required=True, index=True)
    db_name_id = fields.Many2one(
        'machine.db.name', "Database Name", required=True,)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, db_name_id)',
            _('The name must be unique per Database Name !')
        ),
    ]


class MachineDbName(models.Model):
    """Model representing database name.

    E.g. PostgreSQL, MySQL.
    """

    _name = 'machine.db.name'
    _description = 'Machine Database Name'

    name = fields.Char(required=True, index=True)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name)',
            _('The name must be unique !')
        ),
    ]


class MachineOs(models.Model):
    """Model representing operating systems."""

    _name = 'machine.os'
    _description = 'Machine OS'

    name = fields.Char("Version", required=True, index=True)
    os_name_id = fields.Many2one('machine.os.name', "OS Name", required=True,)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, os_name_id)',
            _('The name must be unique per OS Name !')
        ),
    ]


class MachineOsName(models.Model):
    """Model representing operating system name.

    E.g. Ubuntu, Red Hat, Windows.
    """

    _name = 'machine.os.name'
    _description = 'Machine OS Name'

    name = fields.Char(required=True, index=True)
    os_type_id = fields.Many2one('machine.os.type', "OS Type", required=True)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, os_type_id)',
            _('The name must be unique per OS Type !')
        ),
    ]


class MachineOsType(models.Model):
    """Model representing operating system type.

    E.g. Linux, Unix, Windows.
    """

    _name = 'machine.os.type'
    _description = 'Machine OS Type'

    name = fields.Char(required=True,)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('The name must be unique !')),
    ]
