from django.db import IntegrityError, transaction
from django.test import TestCase

from dataportal.models import MainProject, Project, Telescope


class ProjectHierarchyTest(TestCase):
    def test_telescope_can_have_multiple_main_projects(self):
        telescope = Telescope.objects.create(name="Synthetic Scope")
        first = MainProject.objects.create(name="First", telescope=telescope)
        second = MainProject.objects.create(name="Second", telescope=telescope)

        self.assertEqual(list(telescope.main_projects.order_by("id")), [first, second])

    def test_project_requires_main_project(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Project.objects.create(code="SYNTHETIC", short="SYNTH", main_project=None)
