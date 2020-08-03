import pytest
from dataportal.views import IndexView


@pytest.mark.django_db
def test_login(client, django_user_model):
    username = "buffy"
    password = "summers1"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    response = client.get("/meertime/")
    assert response.status_code == 200
    assert response.template_name == ["dataportal/index.html", "dataportal/observations_list.html"]


def test_login_redirect(client):
    response = client.get("/meertime/")
    assert response.status_code == 302
