import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Programs
from .types import ProgramsInput, ProgramsType


class CreateProgram(graphene.Mutation):
    class Arguments:
        input = ProgramsInput(required=True)

    ok = graphene.Boolean()
    program = graphene.Field(ProgramsType)

    @classmethod
    @permission_required("dataportal.add_programs")
    def mutate(cls, self, info, input):
        ok = True
        program, _ = Programs.objects.get_or_create(**input.__dict__)
        return CreateProgram(ok=ok, program=program)


class UpdateProgram(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProgramsInput(required=True)

    ok = graphene.Boolean()
    program = graphene.Field(ProgramsType)

    @classmethod
    @permission_required("dataportal.add_programs")
    def mutate(cls, self, info, id, input):
        try:
            program = Programs.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(program, key, val)
            program.save()
            return UpdateProgram(program=program)
        except:
            return UpdateProgram(program=None)


class DeleteProgram(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_programs")
    def mutate(cls, self, info, id):
        Programs.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
