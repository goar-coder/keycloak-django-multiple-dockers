import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.test import RequestFactory
from django.views import View

from accounts.mixins import GroupRequiredMixin

User = get_user_model()


class _AllowedGroupsView(GroupRequiredMixin, View):
    allowed_groups = ['pl:viewer']

    def get(self, request, *args, **kwargs):
        return HttpResponse('ok', status=200)


class _MultiGroupsView(GroupRequiredMixin, View):
    allowed_groups = ['pl:editor', 'pl:admin']

    def get(self, request, *args, **kwargs):
        return HttpResponse('ok', status=200)


class _NoGroupsConfiguredView(GroupRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('ok', status=200)


@pytest.fixture
def rf():
    return RequestFactory()


def test_allows_user_with_matching_group(rf, db):
    user = User.objects.create_user(username='grp-user-pl')
    g, _ = Group.objects.get_or_create(name='pl:viewer')
    user.groups.add(g)
    request = rf.get('/reports/')
    request.user = user
    assert _AllowedGroupsView.as_view()(request).status_code == 200


def test_denies_user_without_group(rf, db):
    user = User.objects.create_user(username='no-grp-pl')
    request = rf.get('/reports/')
    request.user = user
    response = _AllowedGroupsView.as_view()(request)
    assert response.status_code == 302
    assert '/group-denied/' in response['Location']
    assert 'pl:viewer' in response['Location']


def test_redirects_unauthenticated(rf, db):
    request = rf.get('/editor/')
    request.user = AnonymousUser()
    response = _AllowedGroupsView.as_view()(request)
    assert response.status_code == 302
    assert 'oidc/authenticate' in response['Location'] or 'login' in response['Location'].lower()


def test_or_logic_allows_any(rf, db):
    user = User.objects.create_user(username='editor-user')
    g, _ = Group.objects.get_or_create(name='pl:editor')
    user.groups.add(g)
    request = rf.get('/editor/')
    request.user = user
    assert _MultiGroupsView.as_view()(request).status_code == 200


def test_raises_when_allowed_groups_not_configured(rf, db):
    user = User.objects.create_user(username='misconfigured-user')
    request = rf.get('/somewhere/')
    request.user = user
    with pytest.raises(ImproperlyConfigured):
        _NoGroupsConfiguredView.as_view()(request)
