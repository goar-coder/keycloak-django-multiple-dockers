import pytest
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model

from accounts.backends import PoliciesOIDCBackend

User = get_user_model()


@pytest.fixture
def backend():
    return PoliciesOIDCBackend()


def test_sync_pl_groups_assigns_auth_group(db, backend):
    user = User.objects.create_user(username='pl-user-001')
    backend._sync_pl_groups(user, {'groups': ['pl:viewer']})
    assert user.groups.filter(name='pl:viewer').exists()


def test_sync_pl_groups_ignores_d1_groups(db, backend):
    user = User.objects.create_user(username='pl-user-002')
    backend._sync_pl_groups(user, {'groups': ['d1:admin', 'pl:editor']})
    assert not user.groups.filter(name='d1:admin').exists()
    assert user.groups.filter(name='pl:editor').exists()


def test_sync_pl_groups_clears_removed_groups(db, backend):
    from django.contrib.auth.models import Group
    user = User.objects.create_user(username='pl-user-003')
    g, _ = Group.objects.get_or_create(name='pl:viewer')
    user.groups.add(g)
    backend._sync_pl_groups(user, {'groups': []})
    assert not user.groups.filter(name='pl:viewer').exists()


def test_sync_ignores_non_prefixed_groups(db, backend):
    user = User.objects.create_user(username='pl-user-004')
    backend._sync_pl_groups(user, {'groups': ['team-a', 'ops', 'pl:admin']})
    assert not user.groups.filter(name='team-a').exists()
    assert not user.groups.filter(name='ops').exists()
    assert user.groups.filter(name='pl:admin').exists()


def test_create_user_syncs_pl_groups(db, backend):
    claims = {
        'sub': 'pl-new-001',
        'email': 'new@pl.com',
        'groups': ['pl:admin'],
    }
    with patch.object(backend, 'get_userinfo', return_value=claims):
        user = backend.create_user(claims)
    assert user.groups.filter(name='pl:admin').exists()


def test_update_user_syncs_pl_groups(db, backend):
    user = User.objects.create_user(username='pl-update-001')
    backend.update_user(user, {'groups': ['pl:editor']})
    assert user.groups.filter(name='pl:editor').exists()
