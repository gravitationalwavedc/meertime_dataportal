import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Sessions
from .types import SessionsInput, SessionsType


class CreateSession(graphene.Mutation):
    class Arguments:
        input = SessionsInput(required=True)

    ok = graphene.Boolean()
    session = graphene.Field(SessionsType)

    @classmethod
    @permission_required("dataportal.add_sessions")
    def mutate(cls, self, info, input):
        ok = True
        session, _ = Sessions.objects.get_or_create(**input.__dict__)
        return CreateSession(ok=ok, session=session)


class UpdateSession(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = SessionsInput(required=True)

    ok = graphene.Boolean()
    session = graphene.Field(SessionsType)

    @classmethod
    @permission_required("dataportal.add_sessions")
    def mutate(cls, self, info, id, input):
        try:
            session = Sessions.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(session, key, val)
            session.save()
            return UpdateSession(session=session)
        except:
            return UpdateSession(session=None)


class DeleteSession(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_sessions")
    def mutate(cls, self, info, id):
        Sessions.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_session = CreateSession.Field()
    update_session = UpdateSession.Field()
    delete_session = DeleteSession.Field()
