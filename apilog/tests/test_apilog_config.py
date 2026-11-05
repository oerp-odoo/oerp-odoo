from .. import value_objects as vo
from . import common


class TestApilogConfig(common.TestApilogCommon):
    def _create_config(self, **kwargs):
        vals = {
            'name': "AC-CFG-1",
            'direction': vo.RequestDirection.INCOMING,
            'source': 'wsgi',
            'match_expression': 'True',
            'active': True,
        }
        vals.update(kwargs)
        return self.ApilogConfig.create(vals)

    def test_01_has_any_config_no_config(self):
        """Check has_any_config is false when there are no configs."""
        # GIVEN
        # No config exists.
        # WHEN
        result = self.ApilogConfig.has_any_config()
        # THEN
        self.assertFalse(result)

    def test_02_has_any_config_after_create(self):
        """Check cached has_any_config is invalidated by config creation."""
        # GIVEN
        self.assertFalse(self.ApilogConfig.has_any_config())
        # WHEN
        self._create_config()
        # THEN
        self.assertTrue(self.ApilogConfig.has_any_config())

    def test_03_has_any_config_after_deactivate(self):
        """Check cached has_any_config is invalidated by config deactivation."""
        # GIVEN
        config = self._create_config()
        self.assertTrue(self.ApilogConfig.has_any_config())
        # WHEN
        config.active = False
        # THEN
        self.assertFalse(self.ApilogConfig.has_any_config())
