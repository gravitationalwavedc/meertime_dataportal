from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'email',
        'password',
        'status',
        'verification_code',
        'verification_expiry',
        'created',
    ]

    # def save_model(self, request, obj, form, change):
    #     update_fields = []
    #
    #     if change:
    #         if form.initial['status'] != form.cleaned_data['status']:
    #             update_fields.append('status')
    #
    #     obj.save(update_fields=update_fields)


# admin.site.register(Registration)
