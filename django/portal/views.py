from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from accounts.decorators import require_groups


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pl_groups'] = [g.name for g in self.request.user.groups.filter(name__startswith='pl:')]
        return ctx


class GroupAccessDeniedView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/group_access_denied.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        raw = self.request.GET.get('required', '')
        ctx['required_groups'] = [g for g in raw.split(',') if g]
        return ctx


@method_decorator(require_groups(['pl:report']), name='dispatch')
class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/reports.html'


@method_decorator(require_groups(['pl:data', 'pl:admin', 'admin:data']), name='dispatch')
class DataView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/data.html'


@method_decorator(require_groups(['pl:editor', 'pl:admin']), name='dispatch')
class EditorView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/editor.html'


@method_decorator(require_groups(['pl:admin']), name='dispatch')
class PoliciesAdminView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/admin_section.html'
