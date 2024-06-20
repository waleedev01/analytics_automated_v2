import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analytics_automated_project.settings.dev')
django.setup()

from analytics_automated.cwl_parser import read_cwl_file
from analytics_automated.models import Backend


def add_fake_backend(name, root_path):
    b = Backend.objects.create(name=name)
    # b.queue_type = queue_type
    b.root_path = root_path
    b.save()
    return b


if __name__ == '__main__':
    # this_backend = add_fake_backend(name="local1", root_path="/tmp/")
    base_dir = '../analytics_automated/'
    file_path = os.path.join(base_dir, 'tests', 'example_cwl_file', 'memembed.cwl')
    result = read_cwl_file(file_path)