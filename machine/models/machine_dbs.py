from odoo import models, fields, _


class MachineDbsInstance(models.Model):
    """Model representing database management system instance.

    You can specify databases, users and other details on that instance.
    """

    _name = 'machine.dbs.instance'
    _description = "Machine Instance Database System"

    name = fields.Char(required=True,)
    dbs_id = fields.Many2one('machine.dbs', "Database System", required=True)
    machine_instance_id = fields.Many2one(
        'machine.instance', "Machine Instance", required=True)
    dbs_instance_user_ids = fields.One2many(
        'machine.dbs.instance.user', 'dbs_instance_id', "DBS Users")
    dbs_instance_db_ids = fields.One2many(
        'machine.dbs.instance.database', 'dbs_instance_id', "Databases")
    port = fields.Integer(required=True,)
    # TODO: add possibility to specify users and databases.
    amount_users = fields.Integer("Users Count")
    amount_databases = fields.Integer("Databases Count")


class MachineInstanceDbsUser(models.Model):
    """Model representing database system users on instance."""

    _name = 'machine.dbs.instance.user'
    _description = 'Machine Instance DBS Users'
    _rec_name = 'username'

    username = fields.Char("Username", required=True)
    dbs_instance_id = fields.Many2one(
        'machine.dbs.instance', "Database System Instance")


class MachineInstanceDbsDatabase(models.Model):
    """Model representing database for database system instance."""

    _name = 'machine.dbs.instance.database'
    _description = 'Machine Instance DBS Database'

    name = fields.Char(required=True)
    dbs_instance_id = fields.Many2one(
        'machine.dbs.instance', "Database System Instance", required=True,)


class MachineDbs(models.Model):
    """Model representing specific database system version."""

    _name = 'machine.dbs'
    _description = 'Machine Database System'

    name = fields.Char("Version", required=True, index=True)
    dbs_name_id = fields.Many2one(
        'machine.dbs.name', "Database Name", required=True,)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, dbs_name_id)',
            _('The name must be unique per Database Name !')
        ),
    ]


class MachineDbsName(models.Model):
    """Model representing database name.

    E.g. PostgreSQL, MySQL.
    """

    _name = 'machine.dbs.name'
    _description = 'Machine Database System Name'

    name = fields.Char(required=True, index=True)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name)',
            _('The name must be unique !')
        ),
    ]
