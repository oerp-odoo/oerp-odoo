from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

from .. import value_objects as vo


class ApilogMetadata(models.Model):
    _name = 'apilog.config'
    _description = "API Log Config"
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    match_expression = fields.Char(
        required=True,
        help="Specify expression to match matcher input for logging. "
        + "E.g. `'/my/path' in inp.endpoint`",
    )
    direction = fields.Selection(
        [
            (vo.RequestDirection.INCOMING, "Incoming"),
            (vo.RequestDirection.OUTGOING, "Outgoing"),
        ],
        required=True,
    )
    debug = fields.Boolean(
        help="Whether to log some messages about API Log in general logs"
    )
    source = fields.Selection(
        lambda s: s.prepare_source_selection(), string="Log Source", required=True
    )
    label_ids = fields.Many2many(
        'apilog.label',
        'apilog_config_label_rel',
        'config_id',
        'label_id',
        string="Labels",
        help="Labels to use every time this config is matched",
    )
    config_label_ids = fields.One2many(
        'apilog.config.label',
        'config_id',
        string="Extra Labels",
        help="Labels to include if it matches an expression.",
    )
    log_limit_days = fields.Integer(
        "Days to Keep Logs", default=0, help="0 means no limit."
    )
    log_limit_count = fields.Integer(
        "Maximum Logs Count",
        default=0,
        help="Maximum number of log entries to keep. 0 means no limit.",
    )
    active = fields.Boolean(default=False)
    response_body_as_file = fields.Boolean(string="Save Response Body in File")

    @api.constrains('match_expression')
    def _check_match_expression(self):
        ApilogMatcher = self.env['apilog.matcher']
        for rec in self:
            ApilogMatcher.check_match(rec.match_expression)

    @api.constrains('direction', 'source')
    def _check_source(self):
        src_cfg = self.get_source_config()
        for rec in self:
            directions = src_cfg[rec.source]['directions']
            if rec.direction not in directions:
                src_label = rec.get_selection_label('source')
                dir_label = rec.get_selection_label('direction')
                raise ValidationError(
                    _(
                        "%(src)s can't use %(dir)s direction!",
                        src=src_label,
                        dir=dir_label,
                    )
                )

    @api.model
    def get_source_config(self):
        return {
            'wsgi': {'label': "WSGI", 'directions': (vo.RequestDirection.INCOMING,)}
        }

    @api.model
    def prepare_source_selection(self):
        return [(k, v['label']) for k, v in self.get_source_config().items()]

    @tools.ormcache()
    def has_any_config(self):
        return bool(self.search([], limit=1))

    @tools.ormcache('meta_key')
    def get_apilog_metadata(self, meta_key):
        configs = self._find_configs(meta_key)
        inp = vo.ApilogMatcherInput(
            endpoint=meta_key.endpoint,
            verb=meta_key.verb,
            status_code=meta_key.status_code,
            call_stack=meta_key.call_stack,
            auth_fingerprint=meta_key.auth_fingerprint,
        )
        config = configs._match_config(inp)
        if not config:
            return None
        labels = config._get_labels(inp)
        return vo.ApilogMetadata(
            cfg_id=config.id,
            direction=config.direction,
            source=config.source,
            label_ids=labels.ids,
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env.registry.clear_cache()
        return records

    def write(self, vals):
        result = super().write(vals)
        self.env.registry.clear_cache()
        return result

    def unlink(self):
        result = super().unlink()
        self.env.registry.clear_cache()
        return result

    def _get_labels(self, inp: vo.ApilogMatcherInput):
        self.ensure_one()
        labels = self.label_ids
        ApilogMatcher = self.env['apilog.matcher']
        for cfg_label in self.config_label_ids:
            if ApilogMatcher.match(cfg_label.match_expression, inp):
                labels |= cfg_label.label_id
        return labels

    def _find_configs(self, meta_key: vo.ApilogMetaKey):
        domain = self._prepare_domain(meta_key)
        return self.search(domain)

    def _match_config(self, inp: vo.ApilogMatcherInput):
        ApilogMatcher = self.env['apilog.matcher']
        for config in self:
            # Note. We only care for the first match!
            if ApilogMatcher.match(config.match_expression, inp):
                return config
        return self.browse()

    @api.model
    def _prepare_domain(self, meta_key: vo.ApilogMetaKey):
        return [
            ('direction', '=', meta_key.direction),
            ('source', '=', meta_key.source),
        ]
