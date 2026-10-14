from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import EquipmentLoanCase


@tagged('post_install', '-at_install')
class TestEquipmentItem(EquipmentLoanCase):

    def test_name_key_ignores_case_spaces_and_punctuation(self):
        cases = [
            ('Beamer-A 7', 'beamera7'),
            ('  USB_Hub #2 ', 'usbhub2'),
            ('Kamera Ü1', 'kameraü1'),
        ]
        for name, expected in cases:
            with self.subTest(name=name):
                self.assertEqual(self.Item.create({'name': name}).name_key, expected)

    def test_near_duplicate_names_are_rejected(self):
        for name in ('test laptop 1', 'TEST-LAPTOP-1', 'testlaptop1', 'Test_Laptop.1'):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                self.Item.create({'name': name})

    def test_similar_but_different_names_are_allowed(self):
        items = self.Item.create([{'name': 'Test Laptop 11'}, {'name': 'Test Laptop 2'}])
        self.assertEqual(len(items), 2)

    def test_renaming_to_existing_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.projector.write({'name': 'test-laptop-1'})

    def test_renaming_item_to_variant_of_own_name_is_allowed(self):
        self.laptop.write({'name': 'TEST LAPTOP 1'})
        self.assertEqual(self.laptop.name_key, 'testlaptop1')

    def test_archived_item_still_blocks_duplicate(self):
        self.laptop.action_archive()
        with self.assertRaises(ValidationError):
            self.Item.create({'name': 'Test Laptop 1'})
