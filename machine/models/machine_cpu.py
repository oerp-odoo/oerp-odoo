from odoo import models, fields


class MachineCpu(models.Model):
    """Model representing CPUs."""

    _name = 'machine.cpu'
    _description = 'Machine CPU'

    name = fields.Char(required=True,)
    cpu_brand_id = fields.Many2one(
        'machine.cpu.brand', "CPU Brand", required=True)
    cores = fields.Integer(required=True, default=2)
    clockspeed = fields.Float("Clockspeed in GHz", required=True)


class MachineCpuBrand(models.Model):
    """Model to show CPU brands."""

    _name = 'machine.cpu.brand'
    _description = 'Machine CPU Brand'

    name = fields.Char(required=True,)
    cpu_vendor_id = fields.Many2one(
        'machine.cpu.vendor', "CPU Vendor", required=True)


class MachineCpuVendor(models.Model):
    """Model to show CPU vendors."""

    _name = 'machine.cpu.vendor'
    _description = 'Machine CPU Vendor'

    name = fields.Char(required=True, index=True)
