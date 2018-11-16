from . import common

from ..utils import generate_name


class Dummy(object):
    """Dummy class to test attribute combinations."""

    def __init__(self, **kwargs):
        """Set up attributes."""
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestGenerateName(common.TestMachineCommon):
    """Class to test generate_name function."""

    def test_generate_name_1(self):
        """Get name using two attributes."""
        # Modify dummy object by adding two attributes.
        dummy = Dummy(a=10, b='test')
        res = generate_name('{a} / {b}', dummy)
        self.assertEqual(res, '10 / test')

    def test_generate_name_2(self):
        """Specify non existing attribute on pattern to raise error."""
        dummy = Dummy(c=5)
        self.assertRaises(
            AttributeError,
            generate_name,
            '{b} / {c}',
            dummy)

    def test_generate_name_3(self):
        """Strip falsy attributes."""
        dummy = Dummy(a=False, b='test')
        dummy.a = False
        res = generate_name('{a} / {b}', dummy, strip_falsy=True)
        self.assertEqual('test', res)

    def test_generate_name_4(self):
        """Do Not strip falsy attributes."""
        dummy = Dummy(a=False, b='test')
        res = generate_name('{a} / {b}', dummy, strip_falsy=False)
        self.assertEqual('False / test', res)

    def test_generate_name_5(self):
        """Get name with attributes of attribute (n-depth access)."""
        dummy = Dummy(c=10)
        dummy2 = Dummy(b=dummy)
        dummy3 = Dummy(a=dummy2, b='something')
        res = generate_name('{a.b.c} | {b}', dummy3, strip_falsy=True)
        self.assertEqual('10 | something', res)
        # Now by make c attr falsy to be stripped away.
        dummy.c = 0
        res = generate_name('{a.b.c} | {b}', dummy3, strip_falsy=True)
        self.assertEqual('something', res)
        # Now do not strip falsy attribute.
        res = generate_name('{a.b.c} | {b}', dummy3, strip_falsy=False)
        self.assertEqual('0 | something', res)
