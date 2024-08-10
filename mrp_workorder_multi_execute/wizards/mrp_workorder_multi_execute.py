from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpWorkorderMultiExecute(models.TransientModel):
    """Wizard to handle multiple workorder actions at once."""

    _name = 'mrp.workorder.multi.execute'
    _description = "MRP Workorder Multi Execute"

    @api.model
    def default_get(self, fields_list):
        workorders = self._get_workorders()
        self.env['mrp.workorder.multi.execute.service']._validate_workorders(workorders)
        return super().default_get(fields_list)

    action = fields.Selection(
        [
            ('start', "Start"),
            ('finish', "Finish"),
            ('pause', "Pause"),
            ('block', "Block"),
            ('unblock', "Unblock"),
        ],
        required=True,
    )
    loss_id = fields.Many2one(
        'mrp.workcenter.productivity.loss',
        string="Loss Reason",
    )
    loss_description = fields.Text("Description")

    def action_execute(self):
        """Execute specified action."""
        self.ensure_one()
        method_name, args, kw = self._prepare_service_method_w_args_kwargs()
        Service = self.env['mrp.workorder.multi.execute.service']
        service_method = getattr(Service, method_name)
        service_method(*args, **kw)
        return True

    def _prepare_service_method_w_args_kwargs(self):
        self.ensure_one()
        workorders = self._get_workorders()
        args = [workorders]
        kw = {}
        # We expect to match action value.
        method_name = self.action
        if self.action == 'block':
            args.append(self.loss_id)
            kw['description'] = self.loss_description
        return (method_name, args, kw)

    @api.model
    def _get_workorders(self):
        active_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')
        if active_model != 'mrp.workorder':
            raise ValidationError(
                _("%s wizard expects mrp.workorder active_model!", self._name)
            )
        return self.env[active_model].browse(active_ids)
