from __future__ import annotations

from odoo import _, models
from odoo.exceptions import ValidationError


class MrpWorkorderMultiExecuteService(models.AbstractModel):
    _name = 'mrp.workorder.multi.execute.service'
    _description = "MRP Workorder Multi Execute Service"

    def start(self, workorders):
        self._validate_workorders(workorders)
        for wo in workorders:
            wo.button_start()
        return True

    def finish(self, workorders):
        self._validate_workorders(workorders)
        workorders.button_finish()
        return True

    def pause(self, workorders):
        self._validate_workorders(workorders)
        for wo in workorders:
            wo.button_pending()
        return True

    def block(self, workorders, productivity_loss, description: str | None = None):
        self._validate_workorders(workorders)
        # All workorders must have same workcenter.
        workcenter = workorders[0].workcenter_id
        # TODO: shouldn't we also include date_end (current time) here too?
        # Though standard blocking also does not include that..
        productivity = self.env['mrp.workcenter.productivity'].create(
            {
                'workcenter_id': workcenter.id,
                'loss_id': productivity_loss.id,
                'description': description or False,
            }
        )
        productivity.button_block()
        return productivity

    def unblock(self, workorders):
        self._validate_workorders(workorders)
        workorders[0].workcenter_id.unblock()
        return True

    def _validate_workorders(self, workorders):
        if not workorders:
            raise ValidationError(
                _("At least one workorder must passed for multi execute service")
            )
        workcenters = workorders.mapped('workcenter_id')
        if len(workcenters) > 1:
            raise ValidationError(
                _("Can only execute workorders with the same workcenter!")
            )
        return True
