import logging

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger('accounts')


class GroupRequiredMixin(AccessMixin):
    allowed_groups: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not self.allowed_groups:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} debe definir 'allowed_groups'."
            )

        if not request.user.groups.filter(name__in=self.allowed_groups).exists():
            required = ','.join(self.allowed_groups)
            logger.info(
                'action=group_denied user=%s required=%s',
                request.user.username, required,
            )
            return redirect(f"{reverse('group-access-denied')}?required={required}")

        return super().dispatch(request, *args, **kwargs)
