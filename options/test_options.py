from unittest import TestCase
from .options import Option

class TestOption(TestCase):
    def test_toogle_selection(self):
        option = Option(None, ' this is a text', 10, status=0)

        for s in range(0, 3):
            option.status = s

            if s == 0:
                self.assertFalse(option.selected)
                option.toogle_selection()
                self.assertTrue(option.selected)
                self.assertEqual(option.status, 1)
            elif s == 1:
                self.assertTrue(option.selected)
                option.toogle_selection()
                self.assertFalse(option.selected)
                self.assertEqual(option.status, 0)
            elif s == 2:
                self.assertFalse(option.selected)
                option.toogle_selection()
                self.assertTrue(option.selected)
                self.assertEqual(option.status, 3)
            elif s == 3:
                self.assertTrue(option.selected)
                option.toogle_selection()
                self.assertFalse(option.selected)
                self.assertEqual(option.status, 2)
            else:
                self.fail('status test input out of range')
