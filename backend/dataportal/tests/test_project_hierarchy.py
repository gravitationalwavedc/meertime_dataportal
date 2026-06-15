from django.db import IntegrityError, transaction
from django.test import TestCase

from dataportal.models import MainProject, Project, Telescope


class ProjectHierarchyTest(TestCase):
    def test_telescope_has_only_one_main_project(self):
        telescope = Telescope.objects.create(name="Synthetic Scope")
        MainProject.objects.create(name="First", telescope=telescope)

        with self.assertRaises(IntegrityError), transaction.atomic():
            MainProject.objects.create(name="Second", telescope=telescope)

    def test_project_requires_main_project(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Project.objects.create(code="SYNTHETIC", short="SYNTH", main_project=None)
