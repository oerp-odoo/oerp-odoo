import datetime
import logging
from warnings import warn

from odoo import api, models
from odoo.fields import Domain

from .. import value_objects as vo

_logger = logging.getLogger(__name__)


class HttpClientLogRotation(models.AbstractModel):
    _name = 'http.client.log.rotation'
    _description = "HTTP Client Log Rotation"

    @property
    def _log_model(self):
        return self.env['http.client.log']

    def rotate(self, cfg: vo.Config):
        warn(
            "Http Client Logging feature is deprecated and will be removed soon.",
            DeprecationWarning,
            stacklevel=2,
        )
        log_cfg = cfg.log
        limit_count = log_cfg.limit_count
        deleted_cnt = 0
        if limit_count:
            deleted_cnt += self._rotate_by_limit(limit_count, cfg.controller_model)
        limit_days = log_cfg.limit_days
        if limit_days:
            deleted_cnt += self._rotate_by_days(limit_days, cfg.controller_model)
        return deleted_cnt

    @api.autovacuum
    def _gc_rotate(self):
        # A bit redundant that we find models and then config data..:)
        HttpClientConfig = self.env['http.client.config']
        for config in HttpClientConfig.search([]):
            model_name = config.model_controller_id.model
            deleted_cnt = self.rotate(HttpClientConfig.get_cfg(model_name))
            if deleted_cnt:
                _logger.info("Deleted %s log records for %s", deleted_cnt, model_name)

    def _rotate_by_limit(self, limit: int, controller_model: str):
        domain = self._prepare_domain_common(controller_model)
        count = self._log_model.search_count(domain)
        # No need to rotate.
        if count <= limit:
            return 0
        count_to_del = count - limit
        # Must delete from oldest to newest.
        logs = self._log_model.search(domain, limit=count_to_del, order='id')
        logs.unlink()
        return count_to_del

    def _rotate_by_days(self, days: int, controller_model: str):
        domain = self._prepare_domain_by_days(days, controller_model)
        logs = self._log_model.search(domain)
        logs_count = len(logs)
        logs.unlink()
        return logs_count

    def _prepare_domain_common(self, controller_model: str):
        return [('model_controller_id.model', '=', controller_model)]

    def _prepare_domain_by_days(self, days: int, controller_model: str):
        domain = self._prepare_domain_common(controller_model)
        dt = datetime.datetime.now() - datetime.timedelta(days)
        return Domain.AND([domain, [('create_date', '<', dt)]])
