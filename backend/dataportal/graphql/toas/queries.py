from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Toas


class ToasNode(DjangoObjectType):
    class Meta:
        model = Toas
        filter_fields = {
            "processing_id": ["exact"],
            "input_folding_id": ["exact"],
            "timing_ephemeris_id": ["exact"],
            "template_id": ["exact"],
        }
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    toa = relay.Node.Field(ToasNode)
    all_toas = DjangoFilterConnectionField(ToasNode, max_limit=10000)
