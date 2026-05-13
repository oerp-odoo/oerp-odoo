import datetime
import logging

from odoo import api, models
from odoo.fields import Domain

from ..value_objects import ApilogRotatorConfig

_logger = logging.getLogger(__name__)


class ApilogRotator(models.AbstractModel):
    _name = 'apilog.rotator'
    _description = "API Log Rotator"

    @property
    def _log_model(self):
        return self.env['apilog.log']

    def rotate(self, cfg: ApilogRotatorConfig):
        limit_count = cfg.limit_count
        deleted_cnt = 0
        if limit_count:
            deleted_cnt += self._rotate_by_limit(limit_count, cfg.apilog_cfg_id)
        limit_days = cfg.limit_days
        if limit_days:
            deleted_cnt += self._rotate_by_days(limit_days, cfg.apilog_cfg_id)
        return deleted_cnt

    @api.autovacuum
    def _gc_rotate(self):
        ApilogConfig = self.env['apilog.config']
        for apilog_config in ApilogConfig.search([]):
            deleted_cnt = self.rotate(
                ApilogRotatorConfig.from_apilog_config(apilog_config)
            )
            if deleted_cnt:
                _logger.info(
                    "Deleted %s log records for %s", deleted_cnt, apilog_config.name
                )

    def _rotate_by_limit(self, limit: int, apilog_cfg_id: int):
        domain = self._prepare_domain_common(apilog_cfg_id)
        count = self._log_model.search_count(domain)
        # No need to rotate.
        if count <= limit:
            return 0
        count_to_del = count - limit
        # Must delete from oldest to newest.
        logs = self._log_model.search(domain, limit=count_to_del, order='id')
        logs.unlink()
        return count_to_del

    def _rotate_by_days(self, days: int, apilog_cfg_id: int):
        domain = self._prepare_domain_by_days(days, apilog_cfg_id)
        logs = self._log_model.search(domain)
        logs_count = len(logs)
        logs.unlink()
        return logs_count

    def _prepare_domain_common(self, apilog_cfg_id: int):
        return Domain('config_id', '=', apilog_cfg_id)

    def _prepare_domain_by_days(self, days: int, apilog_cfg_id: int):
        domain = self._prepare_domain_common(apilog_cfg_id)
        dt = datetime.datetime.now() - datetime.timedelta(days)
        return domain & Domain('create_date', '<', dt)
