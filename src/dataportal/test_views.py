import pytest
from .models import Proposals, Pulsars


def login_buffy(client, django_user_model):
    username = "buffy"
    password = "summers1"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)


# Test IndexView
@pytest.mark.django_db
def test_index_view_unauthenticated(client):
    """IndexView should redirect unauthenticated users to the login page."""
    response = client.get("/meertime/")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/meertime/"


@pytest.mark.django_db
def test_index_view_authenticated(client, django_user_model):
    """IndexView should display the index template for authenticated users."""
    login_buffy(client, django_user_model)
    response = client.get("/meertime/")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/index.html", "dataportal/pulsars_list.html"]


@pytest.mark.django_db
def test_index_view_authenticated_with_project_id(client, django_user_model):
    """IndexView should display the correct template when given a project id."""
    login_buffy(client, django_user_model)
    proposal_id = Proposals.objects.create().id
    response = client.get("/meertime/", {"project_id": proposal_id})
    assert response.status_code == 200
    assert response.template_name == ["dataportal/index.html", "dataportal/pulsars_list.html"]


# Test SearchmodeView
@pytest.mark.django_db
def test_search_view_unauthenticated(client):
    """IndexView should redirect unauthenticated users to the login page."""
    response = client.get("/meertime/search/")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/meertime/search/"


@pytest.mark.django_db
def test_search_view_authenticated(client, django_user_model):
    """IndexView should display the index template for authenticated users."""
    login_buffy(client, django_user_model)
    response = client.get("/meertime/search/")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


@pytest.mark.django_db
def test_search_view_authenticated_with_project_id(client, django_user_model):
    """IndexView should display the correct template when given a project id."""
    login_buffy(client, django_user_model)
    proposal_id = Proposals.objects.create().id
    response = client.get("/meertime/search/", {"project_id": proposal_id})
    assert response.status_code == 200
    assert response.template_name == ["dataportal/searchmode.html", "dataportal/pulsars_list.html"]


# Test DetailView
@pytest.mark.django_db
def test_detail_view_unauthenticated(client):
    """DetailView should redirect unauthenticated users to the login page."""
    Pulsars.objects.create(jname="J111-2222")
    response = client.get("/meertime/J111-2222")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/meertime/J111-2222"


@pytest.mark.django_db
def test_detail_view_authenticated(client, django_user_model):
    """DetailView should display the correct template for authenticated users when give a job name."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J111-2222")
    response = client.get("/meertime/J111-2222")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/show_single_psr.html", "dataportal/observations_list.html"]


@pytest.mark.django_db
def test_detail_view_accepts_correct_regex(client, django_user_model):
    """DetailView should accept the correct job strings via the url regex."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J111-2222")
    Pulsars.objects.create(jname="J111+2222")
    response_1 = client.get("/meertime/J111-2222")
    response_2 = client.get("/meertime/J111+2222")
    assert response_1.status_code == 200
    assert response_1.template_name == ["dataportal/show_single_psr.html", "dataportal/observations_list.html"]
    assert response_2.status_code == 200
    assert response_2.template_name == ["dataportal/show_single_psr.html", "dataportal/observations_list.html"]


# Test SearchDetailView
@pytest.mark.django_db
def test_search_detail_view_unauthenticated(client):
    """SearchDetailView should redirect unauthenticated users to the login page."""
    Pulsars.objects.create(jname="J111-2222")
    response = client.get("/meertime/search/J111-2222")
    assert response.status_code == 302
    assert response["location"] == "/accounts/login/?next=/meertime/search/J111-2222"


@pytest.mark.django_db
def test_search_detail_view_authenticated(client, django_user_model):
    """SearchDetailView should display the correct template for authenticated users when give a job name."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J111-2222")
    response = client.get("/meertime/search/J111-2222")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]


@pytest.mark.django_db
def test_search_detail_view_accepts_correct_regex(client, django_user_model):
    """SearchDetailView should accept the correct job strings via the url regex."""
    login_buffy(client, django_user_model)
    Pulsars.objects.create(jname="J111-2222")
    Pulsars.objects.create(jname="J111+2222")
    response_1 = client.get("/meertime/search/J111-2222")
    response_2 = client.get("/meertime/search/J111+2222")
    assert response_1.status_code == 200
    assert response_1.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]
    assert response_2.status_code == 200
    assert response_2.template_name == ["dataportal/show_single_psr_search.html", "dataportal/searchmode_list.html"]
