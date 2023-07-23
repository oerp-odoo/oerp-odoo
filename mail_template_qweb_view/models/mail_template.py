from odoo import api, fields, models


class MailTemplate(models.Model):
    """Extend to add qweb_view engine option for body_html."""

    _inherit = 'mail.template'

    body_engine = fields.Selection(
        [('qweb', "QWeb"), ('qweb_view', "QWeb View")],
        default='qweb',
    )
    view_body_qweb_id = fields.Many2one(
        'ir.ui.view',
        domain=[('type', '=', 'qweb')],
        string="QWeb View",
    )
    view_qweb_arch_base = fields.Text(
        related='view_body_qweb_id.arch_base', readonly=False
    )

    def _render_field(
        self,
        field,
        res_ids,
        engine='inline_template',
        compute_lang=False,
        set_lang=False,
        add_context=None,
        options=None,
        post_process=False,
    ):
        if field == 'body_html' and self.body_engine == 'qweb_view':
            self = self.with_context(
                body_engine_data={
                    # Must pass engine val via context, because `engine`
                    # param in this method is useless. Value is always
                    # changed inside method..
                    'engine': 'qweb_view',
                    'template_src': self.view_body_qweb_id.xml_id,
                }
            )
        return super()._render_field(
            field,
            res_ids,
            engine=engine,
            compute_lang=compute_lang,
            set_lang=set_lang,
            add_context=add_context,
            options=options,
            post_process=post_process,
        )

    @api.model
    def _render_template(
        self,
        template_src,
        model,
        res_ids,
        engine='inline_template',
        add_context=None,
        options=None,
        post_process=False,
    ):
        body_engine_data = self._context.get('body_engine_data')
        if body_engine_data:
            template_src = body_engine_data['template_src']
            engine = body_engine_data['engine']
            # Unset it, to not be reused for unrelated calls.
            body_engine_data.clear()
        return super()._render_template(
            template_src,
            model,
            res_ids,
            engine=engine,
            add_context=add_context,
            options=options,
            post_process=post_process,
        )
