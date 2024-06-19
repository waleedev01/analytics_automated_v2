import os
from django.test import TestCase
from analytics_automated.cwl_parser import read_cwl_file
from analytics_automated.models import Backend


def add_fake_backend(name, root_path):
    b = Backend.objects.create(name=name)
    # b.queue_type = queue_type
    b.root_path = root_path
    b.save()
    return b


class CWLParserTest(TestCase):
    def test_read_cwl_file(self):
        """
        Test if the CWL file is read correctly.
        """
        this_backend = add_fake_backend(name="local1", root_path="/tmp/")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'tests', 'example_cwl_file', 'memembed.cwl')
        result = read_cwl_file(file_path)
        # self.assertIsNotNone(result)

    def tearDown(self):
        pass
