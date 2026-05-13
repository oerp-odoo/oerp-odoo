from .common import TestOdootilCommon

UNKNOWN_LANG = 'xx_XX'


class TestNum2Words(TestOdootilCommon):
    """Class to test num2words formating."""

    @classmethod
    def setUpClass(cls):
        """Set up data used in test cases."""
        super().setUpClass()
        cls.currency = cls.env.ref('base.EUR')
        cls.get_num2words = cls.Odootil.get_num2words

    def test_01_get_num2words(self):
        """Test num2words with unknown currency.

        We expect to get an exception because currency with ISO code
        'UNKNOWN_CURRENCY_ISO_CODE' is not implemented in num2words.
        """
        self.currency.name = 'UNKNOWN_CURRENCY_ISO_CODE'
        with self.assertRaises(NotImplementedError):
            self.get_num2words(
                300.0,
                options={
                    'lang': 'en_US',
                    'to': 'currency',
                    'kwargs': {'currency': 'UNKNOWN_CURRENCY_ISO_CODE'},
                },
            )

    def test_02_get_num2words(self):
        """Test num2words with known currency (EUR).

        Here 'known' means currency is implemented in num2words.
        """
        amount_in_words = self.get_num2words(
            300.0,
            options={
                'lang': 'en_US',
                'to': 'currency',
                'kwargs': {'currency': self.currency.name},
            },
        )
        self.assertEqual(
            amount_in_words,
            'three hundred euro, zero cents',
            "Amount in words was not correctly converted!",
        )

    def test_03_get_num2words(self):
        """Test num2words with unknown language."""
        with self.assertRaises(NotImplementedError):
            self.get_num2words(
                300.0,
                options={
                    'lang': UNKNOWN_LANG,
                    'to': 'currency',
                    'kwargs': {'currency': self.currency.name},
                },
            )

    def test_04_get_num2words(self):
        """Check fallback words when can't convert."""
        amount_in_words = self.get_num2words(
            300.0, options={'lang': UNKNOWN_LANG, 'fallback_words': ''}
        )
        self.assertEqual(amount_in_words, '')
        amount_in_words = self.get_num2words(
            300.0,
            options={
                'lang': UNKNOWN_LANG,
                'fallback_words': 'NOT IMPLEMENTED',
            },
        )
        self.assertEqual(amount_in_words, 'NOT IMPLEMENTED')

    def test_05_get_num2words(self):
        """Test num2words with amount only."""
        amount_in_words = self.get_num2words(300.0)
        self.assertEqual(
            amount_in_words,
            'three hundred',
            "Amount in words was not correctly converted!",
        )
