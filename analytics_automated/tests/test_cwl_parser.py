import os
from django.test import TestCase
from analytics_automated.cwl_parser import read_cwl_file


class CWLParserTest(TestCase):

    def test_read_cwl_file(self):
        """
        Test if the CWL file is read correctly.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'tests', 'example_cwl_file', 'memembed.cwl')
        result = read_cwl_file(file_path)
        # self.assertIsNotNone(result)

    def tearDown(self):
        pass
