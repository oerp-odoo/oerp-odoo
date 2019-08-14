from odoo.tests import common


class TestHighlightStyleConfig(common.SavepointCase):
    """Class to test if correct highlight style is used."""

    @classmethod
    def setUpClass(cls):
        """Set up data necessary for style config tests."""
        super(TestHighlightStyleConfig, cls).setUpClass()
        cls.RCS = cls.env['res.config.settings']
        cls.ICP = cls.env['ir.config_parameter']

    def test_01_get_highlight_styles(self):
        """Get existing highlight styles."""
        styles = list(self.RCS._get_highlight_styles())
        self.assertEqual(len(styles), 89)
        self.assertIn('github.css', styles)
        self.assertIn('arta.css', styles)
        self.assertIn('atelier-sulphurpool-dark.css', styles)
        self.assertNotIn('brown-papersq.png', styles)
        self.assertNotIn('not-existing-style.css', styles)

    def test_02_get_active_highlight_style(self):
        """Get default highlight style."""
        style = self.RCS._get_active_highlight_style()
        self.assertEqual(style, 'github.css')

    def test_03_get_active_highlight_style(self):
        """Set new highlight style and check if such is returned."""
        self.ICP.set_param('web_highlight.style', 'arta.css')
        style = self.RCS._get_active_highlight_style()
        self.assertEqual(style, 'arta.css')

    def test_04_get_highlight_style_label(self):
        """Get label for style key. Case: single word."""
        label = self.RCS._get_highlight_style_label('github.css')
        self.assertEqual(label, 'Github')

    def test_05_get_highlight_style_label(self):
        """Get label for style key. Case: multiple word."""
        label = self.RCS._get_highlight_style_label(
            'atelier-sulphurpool-dark.css')
        self.assertEqual(label, 'Atelier Sulphurpool Dark')
