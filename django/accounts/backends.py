import logging

from django.contrib.auth.models import Group
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger('accounts')


class PoliciesOIDCBackend(OIDCAuthenticationBackend):

    def _sync_pl_groups(self, user, claims):
        pl_group_names = [g for g in claims.get('groups', []) if g.startswith('pl:') or g.startswith('admin:')]
        django_groups = []
        for name in pl_group_names:
            group, _ = Group.objects.get_or_create(name=name)
            django_groups.append(group)
        user.groups.set(django_groups)
        logger.info('action=pl_groups_synced user=%s pl_groups=%s', user.username, pl_group_names)

    def create_user(self, claims):
        user = super().create_user(claims)
        user.set_unusable_password()
        user.save(update_fields=['password'])
        self._sync_pl_groups(user, claims)
        return user

    def update_user(self, user, claims):
        self._sync_pl_groups(user, claims)
        return user
