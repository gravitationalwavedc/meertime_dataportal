import pytest
from .models import Proposals, Pulsars


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


@pytest.mark.django_db
def test_index_view_authenticated_with_project_id(client, django_user_model):
    """IndexView should display the correct template when given a project id."""
    login_buffy(client, django_user_model)
    proposal_id = Proposals.objects.create().id
    response = client.get("", {"project_id": proposal_id})
    assert response.status_code == 200
    assert response.template_name == ["dataportal/index.html", "dataportal/pulsars_list.html"]


# Test SearchmodeView
@pytest.mark.django_db
def test_search_view_unauthenticated(client):
    """IndexView should redirect unauthenticated users to the login page."""
    response = client.get("/search/")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/search/"


@pytest.mark.django_db
def test_search_view_authenticated(client, django_user_model):
    """IndexView should display the index template for authenticated users."""
    login_buffy(client, django_user_model)
    response = client.get("/search/")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


@pytest.mark.django_db
def test_search_view_authenticated_with_project_id(client, django_user_model):
    """IndexView should display the correct template when given a project id."""
    login_buffy(client, django_user_model)
    proposal_id = Proposals.objects.create().id
    response = client.get("/search/", {"project_id": proposal_id})
    assert response.status_code == 200
    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


# Test PulsarDetailView
@pytest.mark.django_db
def test_detail_view_unauthenticated(client):
    """PulsarDetailView should redirect unauthenticated users to the login page."""
    Pulsars.objects.create(jname="J1111-2222")
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
    assert response.template_name == ["dataportal/show_single_psr.html", "dataportal/observations_list.html"]


@pytest.mark.django_db
def test_detail_view_accepts_correct_regex(client, django_user_model):
    """PulsarDetailView should accept the correct job strings via the url regex."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J1111-2222")
    Pulsars.objects.create(jname="J1111+2222")
    response_1 = client.get("/J1111-2222")
    response_2 = client.get("/J1111+2222")
    assert response_1.status_code == 200
    assert response_1.template_name == ["dataportal/show_single_psr.html", "dataportal/observations_list.html"]
    assert response_2.status_code == 200
    assert response_2.template_name == ["dataportal/show_single_psr.html", "dataportal/observations_list.html"]


# Test SearchDetailView
@pytest.mark.django_db
def test_search_detail_view_unauthenticated(client):
    """SearchDetailView should redirect unauthenticated users to the login page."""
    Pulsars.objects.create(jname="J1111-2222")
    response = client.get("/search/J1111-2222")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/search/J1111-2222"


@pytest.mark.django_db
def test_search_detail_view_authenticated(client, django_user_model):
    """SearchDetailView should display the correct template for authenticated users when give a job name."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J1111-2222")
    response = client.get("/search/J1111-2222")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]


@pytest.mark.django_db
def test_search_detail_view_accepts_correct_regex(client, django_user_model):
    """SearchDetailView should accept the correct job strings via the url regex."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J1111-2222")
    Pulsars.objects.create(jname="J1111+2222")
    response_1 = client.get("/search/J1111-2222")
    response_2 = client.get("/search/J1111+2222")
    assert response_1.status_code == 200
    assert response_1.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]
    assert response_2.status_code == 200
    assert response_2.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]
