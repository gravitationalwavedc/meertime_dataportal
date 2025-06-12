import graphene

from dataportal.graphql.queries import ToaNode
from dataportal.models import Toa
from user_manage.graphql.decorators import permission_required


class ToaInput(graphene.InputObjectType):
    # foreign keys
    pipelineRunId = graphene.Int(required=True)
    projectShort = graphene.String(required=True)

    ephemerisText = graphene.String(required=True)
    templateId = graphene.Int(required=True)

    toaLines = graphene.List(graphene.String, required=True)

    dmCorrected = graphene.Boolean(required=True)
    nsubType = graphene.String(required=True)
    obsNpol = graphene.Int(required=True)
    obsNchan = graphene.Int(required=True)


class CreateToaOutput(graphene.ObjectType):
    toa = graphene.List(ToaNode)


class CreateToa(graphene.Mutation):
    class Arguments:
        input = ToaInput(required=True)

    toa = graphene.List(ToaNode)
    Output = CreateToaOutput

    @permission_required("dataportal.add_toa")
    def mutate(root, info, input):
        created_toas = Toa.bulk_create(
            pipeline_run_id=input["pipelineRunId"],
            project_short=input["projectShort"],
            template_id=input["templateId"],
            ephemeris_text=input["ephemerisText"],
            toa_lines=input["toaLines"],
            dm_corrected=input["dmCorrected"],
            nsub_type=input["nsubType"],
            npol=input["obsNpol"],
            nchan=input["obsNchan"],
        )
        return CreateToaOutput(toa=created_toas)


class UpdateToa(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ToaInput(required=True)

    toa = graphene.Field(ToaNode)

    @permission_required("dataportal.add_toa")
    def mutate(root, info, id, input):
        try:
            toa = Toa.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(toa, key, val)
            toa.save()
            return UpdateToa(toa=toa)
        except Exception:
            return UpdateToa(toa=None)


class DeleteToa(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @permission_required("dataportal.add_toa")
    def mutate(root, info, id):
        Toa.objects.get(pk=id).delete()
        return DeleteToa(ok=True)


class Mutation(graphene.ObjectType):
    create_toa = CreateToa.Field()
    update_toa = UpdateToa.Field()
    delete_toa = DeleteToa.Field()
