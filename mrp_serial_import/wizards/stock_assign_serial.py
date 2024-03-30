import base64
import csv
import io
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import UserError

DELIMITER = ','


def _update_vals(dct, src_val, target_val):
    for k, v in dct.items():
        if v == src_val:
            dct[k] = target_val


class StockAssignSerial(models.TransientModel):
    """Extend to implement serial numbers import via file."""

    _inherit = 'stock.assign.serial'

    serial_numbers_file = fields.Binary("Serial Numbers File")
    serial_numbers_filename = fields.Char()
    _serial_numbers_file_data = fields.Char()

    @property
    def serial_numbers_file_data(self):
        """Safely eval saved string."""
        self.ensure_one()
        if self._serial_numbers_file_data:
            return literal_eval(self._serial_numbers_file_data)
        return {}

    @property
    def _self_with_serial_numbers_file_data_ctx(self):
        data = self.serial_numbers_file_data
        if data:
            return self.with_context(serial_numbers_file_data=data)
        return self

    def _read_serial_numbers_file_row(self):
        bdata = base64.b64decode(self.serial_numbers_file)
        sdata = bdata.decode()
        for row in csv.DictReader(io.StringIO(sdata), delimiter=DELIMITER):
            yield row

    def _parse_serial_numbers_file(self):
        data = {}
        for row in self._read_serial_numbers_file_row():
            try:
                key = row.pop('name')
                # Empty string is saved as False value, so we convert it
                # to match Odoo expected format.
                _update_vals(row, '', False)
                data[key] = row
            except KeyError:
                raise UserError(_("Serial Numbers Import file expects 'name' column!"))
        return data

    @api.onchange('serial_numbers_file')
    def _onchange_serial_numbers_file(self):
        if self.serial_numbers_file:
            data = self._parse_serial_numbers_file()
            serial_numbers = list(data.keys())
            self.update(
                {
                    'next_serial_number': serial_numbers[0],
                    'serial_numbers': '\n'.join(serial_numbers),
                    '_serial_numbers_file_data': str(data),  # serialize data
                }
            )

    def apply(self):
        """Extend to pass serial numbers extra data via ctx."""
        self = self._self_with_serial_numbers_file_data_ctx
        return super(StockAssignSerial, self).apply()

    def create_backorder(self):
        """Extend to pass serial numbers extra data via ctx."""
        self = self._self_with_serial_numbers_file_data_ctx
        return super(StockAssignSerial, self).create_backorder()

    def no_backorder(self):
        """Extend to pass serial numbers extra data via ctx."""
        self = self._self_with_serial_numbers_file_data_ctx
        return super(StockAssignSerial, self).no_backorder()
