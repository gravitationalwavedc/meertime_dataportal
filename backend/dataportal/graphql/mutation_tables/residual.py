import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required
from decimal import Decimal, getcontext


from dataportal.models import Pulsar, Ephemeris, Project, Residual, Toa


class ResidualType(DjangoObjectType):
    class Meta:
        model = Residual


class ResidualInput(graphene.InputObjectType):
    # foreign keys
    pulsar       = graphene.String(required=True)
    projectShort = graphene.String(required=True)
    ephemerisId  = graphene.Int(required=True)

    residualLines = graphene.List(graphene.String, required=True)


class CreateResidualOutput(graphene.ObjectType):
    residual = graphene.List(ResidualType)


class CreateResidual(graphene.Mutation):
    class Arguments:
        input = ResidualInput(required=True)

    residual = graphene.List(ResidualType)
    Output = CreateResidualOutput

    @classmethod
    @permission_required("dataportal.add_residual")
    def mutate(cls, self, info, input):
        # Get foreign keys
        pulsar    = Pulsar.objects.get(name=input["pulsar"])
        project   = Project.objects.get(short=input["projectShort"])
        ephemeris = Ephemeris.objects.get(id=input["ephemerisId"])

        # MJDs are stored as Decimals as standard floats don't have enough precision
        getcontext().prec = 12

        created_residuals = []
        residual_lines = input["residualLines"]
        for residual_line in residual_lines:
            # Loop over residual lines and and split them to get the important values
            id, mjd, residual, residual_err, residual_phase = residual_line.split(",")
            print(id, mjd, residual, residual_err, residual_phase)
            # Get toa foreign key
            toa = Toa.objects.get(id=int(id))

            # Upload the residual
            residual = Residual.objects.create(
                toa=toa,
                pulsar=pulsar,
                project=project,
                ephemeris=ephemeris,
                # X axis types
                mjd               =Decimal(mjd),
                # binary_orbital_phase=residual_dict["binary_orbital_phase"],
                # Y axis types
                residual_sec      =float(residual),
                residual_sec_err  =float(residual_err),
                residual_phase    =float(residual_phase),
                # residual_phase_err=residual_dict["residual_phase_err"],
            )
            created_residuals.append(residual)
        return CreateResidualOutput(residual=created_residuals)


class UpdateResidual(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ResidualInput(required=True)

    residual = graphene.Field(ResidualType)

    @classmethod
    @permission_required("dataportal.add_residual")
    def mutate(cls, self, info, id, input):
        try:
            residual = Residual.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(residual, key, val)
            residual.save()
            return UpdateResidual(residual=residual)
        except:
            return UpdateResidual(residual=None)


class DeleteResidual(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_residual")
    def mutate(cls, self, info, id):
        Residual.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_residual = CreateResidual.Field()
    update_residual = UpdateResidual.Field()
    delete_residual = DeleteResidual.Field()
