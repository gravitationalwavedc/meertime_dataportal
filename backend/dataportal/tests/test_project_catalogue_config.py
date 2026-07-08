from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase

from dataportal.admin import ProjectAdmin, ProjectAdminForm
from dataportal.models import SUPPORTED_PLOT_TYPES, MainProject, Project, Telescope


class ProjectCatalogueConfigTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        telescope = Telescope.objects.create(name="Synthetic Scope")
        cls.main_project = MainProject.objects.create(name="Synthetic Programme", telescope=telescope)

    def test_catalogue_configuration_defaults(self):
        project = Project.objects.create(code="SYNTHETIC", main_project=self.main_project)

        self.assertFalse(project.is_visible_on_frontend)
        self.assertEqual(project.display_order, 0)
        self.assertEqual(project.band_options, [])
        self.assertEqual(project.plot_types, [])

    def test_supported_band_options_are_valid(self):
        project = Project(code="SYNTHETIC-BANDS", main_project=self.main_project, band_options=["LBAND", "UHF"])

        try:
            project.full_clean()
        except ValidationError as error:
            self.fail(f"Expected supported band options to be valid, but validation failed: {error}")

    def test_band_options_reject_unsupported_values(self):
        project = Project(code="SYNTHETIC", main_project=self.main_project, band_options=["LBAND", "UNKNOWN"])

        with self.assertRaisesRegex(ValidationError, "UNKNOWN"):
            project.full_clean()

    def test_empty_plot_types_are_valid(self):
        project = Project(code="SYNTHETIC-EMPTY", main_project=self.main_project, plot_types=[])

        try:
            project.full_clean()
        except ValidationError as error:
            self.fail(f"Expected empty plot types to be valid, but validation failed: {error}")

    def test_supported_plot_types_are_valid(self):
        project = Project(
            code="SYNTHETIC-SUPPORTED",
            main_project=self.main_project,
            plot_types=["Timing Residuals", "Flux Density", "S/N", "DM", "RM"],
        )

        try:
            project.full_clean()
        except ValidationError as error:
            self.fail(f"Expected supported plot types to be valid, but validation failed: {error}")

    def test_plot_types_reject_unsupported_values(self):
        project = Project(code="SYNTHETIC", main_project=self.main_project, plot_types=["Timing Residuals", "Unknown"])

        with self.assertRaisesRegex(ValidationError, "Unknown"):
            project.full_clean()

    def test_plot_types_help_text_lists_supported_values(self):
        help_text = Project._meta.get_field("plot_types").help_text

        for plot_type in SUPPORTED_PLOT_TYPES:
            self.assertIn(plot_type, help_text)

    def test_admin_uses_checkbox_widgets_for_list_fields(self):
        band_field = ProjectAdminForm.base_fields["band_options"]
        plot_field = ProjectAdminForm.base_fields["plot_types"]

        self.assertIsInstance(band_field.widget, forms.CheckboxSelectMultiple)
        self.assertIsInstance(plot_field.widget, forms.CheckboxSelectMultiple)

    def test_admin_list_exposes_catalogue_controls(self):
        self.assertTrue(
            {"is_visible_on_frontend", "display_order", "band_options", "plot_types"}.issubset(
                ProjectAdmin.list_display
            )
        )
