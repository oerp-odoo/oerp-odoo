from odoo.tests.common import HttpCase


class TestApilogCommon(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ApilogLog = cls.env['apilog.log']
        cls.ApilogMatcher = cls.env['apilog.matcher']
        cls.ApilogConfig = cls.env['apilog.config']
        cls.ApilogLabel = cls.env['apilog.label']
        cls.ApilogHandler = cls.env['apilog.handler']
        cls.ApilogRotator = cls.env['apilog.rotator']
        cls.IrAttachment = cls.env['ir.attachment']
