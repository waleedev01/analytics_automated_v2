from django.test import TestCase, Client
from django.urls import reverse
from analytics_automated.models import Submission, Task, Result, Job, Step

class VisualizationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.job = Job.objects.create(name='test_job')
        self.submission = Submission.objects.create(submission_name='test_submission', job=self.job)
        self.task1 = Task.objects.create(name='task1', description='First task')
        self.task2 = Task.objects.create(name='task2', description='Second task')
        self.step1 = Step.objects.create(job=self.job, task=self.task1, ordering=0)
        self.step2 = Step.objects.create(job=self.job, task=self.task2, ordering=1)
        Result.objects.create(submission=self.submission, task=self.task1, message='completed')
        Result.objects.create(submission=self.submission, task=self.task2, message='running')

    def test_task_states_view(self):
        response = self.client.get(reverse('task_states', args=['test_submission']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('task1', response.json())
        self.assertIn('task2', response.json())

    def test_dashboard_view(self):
        response = self.client.get(reverse('dynamic_visualize'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_static_visualization(self):
        response = self.client.get(reverse('static_visualize'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'workflow_visualization.html')
