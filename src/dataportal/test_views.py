import pytest

# from .models import Proposals, Pulsars, Observations, Utcs
from .models import Pulsars
from datetime import datetime


def login_buffy(client, django_user_model):
    username = "buffy"
    password = "summers1"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)


# Test authentication view template
@pytest.mark.django_db
def test_auth_template(client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200
    assert response.template_name == ["registration/login.html"]


# Test IndexView
@pytest.mark.django_db
def test_index_view_unauthenticated(client):
    """IndexView should redirect unauthenticated users to the login page."""
    response = client.get("")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/"


@pytest.mark.django_db
def test_index_view_authenticated(client, django_user_model):
    """IndexView should display the index template for authenticated users."""
    login_buffy(client, django_user_model)
    response = client.get("")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/index.html", "dataportal/pulsars_list.html"]


# @pytest.mark.django_db
# def test_index_view_authenticated_with_project_id(client, django_user_model):
#    """IndexView should display the correct template when given a project id."""
#    login_buffy(client, django_user_model)
#    proposal_id = Proposals.objects.create().id
#    response = client.get("", {"project_id": proposal_id})
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/index.html", "dataportal/pulsars_list.html"]


# Test SearchmodeView
# @pytest.mark.django_db
# def test_search_view_unauthenticated(client):
#    """IndexView should redirect unauthenticated users to the login page."""
#    response = client.get("/search/")
#    assert response.status_code == 302
#    assert response["location"] == "/accounts/login/?next=/search/"


# @pytest.mark.django_db
# def test_search_view_authenticated(client, django_user_model):
#    """IndexView should display the index template for authenticated users."""
#    login_buffy(client, django_user_model)
#    response = client.get("/search/")
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


# @pytest.mark.django_db
# def test_search_view_authenticated_with_project_id(client, django_user_model):
#    """IndexView should display the correct template when given a project id."""
#    login_buffy(client, django_user_model)
#    proposal_id = Proposals.objects.create().id
#    response = client.get("/search/", {"project_id": proposal_id})
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


# Test PulsarDetailView
@pytest.mark.django_db
def test_detail_view_unauthenticated(client):
    """PulsarDetailView should redirect unauthenticated users to the login page."""
    response = client.get("/J1111-2222")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/J1111-2222"


@pytest.mark.django_db
def test_detail_view_authenticated(client, django_user_model):
    """PulsarDetailView should display the correct template for authenticated users when give a job name."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J1111-2222")
    response = client.get("/J1111-2222")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/show_single_psr.html", "dataportal/foldings_list.html"]


@pytest.mark.django_db
def test_detail_view_accepts_correct_regex(client, django_user_model):
    """PulsarDetailView should accept the correct job strings via the url regex."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J1111-2222")
    Pulsars.objects.create(jname="J1111+2222")
    response_1 = client.get("/J1111-2222")
    response_2 = client.get("/J1111+2222")
    assert response_1.status_code == 200
    assert response_1.template_name == ["dataportal/show_single_psr.html", "dataportal/foldings_list.html"]
    assert response_2.status_code == 200
    assert response_2.template_name == ["dataportal/show_single_psr.html", "dataportal/foldings_list.html"]


# Test SearchDetailView
# @pytest.mark.django_db
# def test_search_detail_view_unauthenticated(client):
#    """SearchDetailView should redirect unauthenticated users to the login page."""
#    Pulsars.objects.create(jname="J1111-2222")
#    response = client.get("/search/J1111-2222")
#    assert response.status_code == 302
#    assert response["location"] == "/accounts/login/?next=/search/J1111-2222"


# @pytest.mark.django_db
# def test_search_detail_view_authenticated(client, django_user_model):
#    """SearchDetailView should display the correct template for authenticated users when give a job name."""
#    login_buffy(client, django_user_model)
#    Pulsars.objects.create(jname="J1111-2222")
#    response = client.get("/search/J1111-2222")
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]


# @pytest.mark.django_db
# def test_search_detail_view_accepts_correct_regex(client, django_user_model):
#    """SearchDetailView should accept the correct job strings via the url regex."""
#    login_buffy(client, django_user_model)
#    Pulsars.objects.create(jname="J1111-2222")
#    Pulsars.objects.create(jname="J1111+2222")
#    response_1 = client.get("/search/J1111-2222")
#    response_2 = client.get("/search/J1111+2222")
#    assert response_1.status_code == 200
#    assert response_1.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]
#    assert response_2.status_code == 200
#    assert response_2.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]


# Test ObservationDetailView
# @pytest.mark.django_db
# def test_obs_detail_view_unauthenticated(client):
#    """ObservationDetailView should redirect unauthenticated users to the login page."""
#    response = client.get("/J1111-2222/2020-10-10-10:10:10/2/")
#    assert response.status_code == 302
#    assert response["location"] == "/accounts/login/?next=/J1111-2222/2020-10-10-10%3A10%3A10/2/"


# @pytest.mark.django_db
# def test_obs_detail_view_authenticated(client, django_user_model):
#    """ObservationDetailView should accept the correct pulsar/utc/beam combination via the url regex."""
#    login_buffy(client, django_user_model)
#
#    psr_str = "J1111-2222"
#    utc_str = "2020-10-10-10:10:10"
#    utc_dt = datetime.strptime(f"{utc_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
#    beam = 2

#    utc = Utcs.objects.create(utc_ts=utc_dt)
#    psr = Pulsars.objects.create(jname=psr_str)
#    Observations.objects.create(pulsar=psr, utc=utc, beam=beam)

#    response = client.get(f"/{psr_str}/{utc_str}/{beam}/")

#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/observation.html"]


# Test TrapumView
@pytest.mark.django_db
def test_trapum_view_unauthenticated(client):
    """TrapumView should redirect unauthenticated users to the login page."""
    response = client.get("/trapum/")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/trapum/"


@pytest.mark.django_db
def test_trapum_view_authenticated(client, django_user_model):
    """TrapumView should display the index template for authenticated users."""
    login_buffy(client, django_user_model)
    response = client.get("/trapum/")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/index.html", "dataportal/pulsars_list.html"]


# @pytest.mark.django_db
# def test_trapum_view_authenticated_with_project_id(client, django_user_model):
#    """TrapumView should display the correct template when given a project id."""
#    login_buffy(client, django_user_model)
#    proposal_id = Proposals.objects.create().id
#    response = client.get("/trapum/", {"project_id": proposal_id})
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/index.html", "dataportal/pulsars_list.html"]


# Test TrapumDetailView
@pytest.mark.django_db
def test_trapum_detail_view_unauthenticated(client):
    """TrapumDetailView should redirect unauthenticated users to the login page."""
    Pulsars.objects.create(jname="J1111-2222")
    response = client.get("/trapum/J1111-2222")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/trapum/J1111-2222"


@pytest.mark.django_db
def test_trapum_detail_view_authenticated(client, django_user_model):
    """TrapumDetailView should display the correct template for authenticated users when give a job name."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J1111-2222")
    response = client.get("/trapum/J1111-2222")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/show_single_psr.html", "dataportal/foldings_list.html"]


@pytest.mark.django_db
def test_trapum_detail_view_accepts_correct_regex(client, django_user_model):
    """TrapumDetailView should accept the correct job strings via the url regex."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J1111-2222")
    Pulsars.objects.create(jname="J1111+2222")
    response_1 = client.get("/trapum/J1111-2222")
    response_2 = client.get("/trapum/J1111+2222")
    assert response_1.status_code == 200
    assert response_1.template_name == ["dataportal/show_single_psr.html", "dataportal/foldings_list.html"]
    assert response_2.status_code == 200
    assert response_2.template_name == ["dataportal/show_single_psr.html", "dataportal/foldings_list.html"]


# Test TrapumSearchmodeView
# @pytest.mark.django_db
# def test_trapum_searchmode_view_unauthenticated(client):
#    """TrapumSearchmodeView should redirect unauthenticated users to the login page."""
#    response = client.get("/trapum/search/")
#    assert response.status_code == 302
#    assert response["location"] == "/accounts/login/?next=/trapum/search/"


# @pytest.mark.django_db
# def test_trapum_searchmode_view_authenticated(client, django_user_model):
#    """TrapumSearchmodeView should display the index template for authenticated users."""
#    login_buffy(client, django_user_model)
#    response = client.get("/trapum/search/")
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


# @pytest.mark.django_db
# def test_trapum_searchmode_view_authenticated_with_project_id(client, django_user_model):
#    """TrapumSearchmodeView should display the correct template when given a project id."""
#    login_buffy(client, django_user_model)
#    proposal_id = Proposals.objects.create().id
#    response = client.get("/trapum/search/", {"project_id": proposal_id})
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


# Test SessionView
# @pytest.mark.django_db
# def test_session_view_unauthenticated(client):
#    """SessionView should redirect unauthenticated users to the login page."""
#    response = client.get("/session/")
#    assert response.status_code == 302
#    assert response["location"] == "/accounts/login/?next=/session/"


# @pytest.mark.django_db
# def test_session_view_authenticated(client, django_user_model):
#    """SessionView should display the index template for authenticated users."""
#    login_buffy(client, django_user_model)
#    response = client.get("/session/")
#    assert response.status_code == 200
#    assert response.template_name == ["dataportal/session.html", "dataportal/observations_list.html"]
