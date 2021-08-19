from django_mysql.models import JSONField
import django_filters


class JSONFieldFilter(django_filters.FilterSet):
    class Meta:
        fields = "__all__"
        filter_overrides = {
            JSONField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            }
        }
