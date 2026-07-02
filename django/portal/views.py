from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from accounts.mixins import GroupRequiredMixin


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


class ReportsView(GroupRequiredMixin, TemplateView):
    template_name = 'portal/reports.html'
    allowed_groups = ['pl:report']


class DataView(GroupRequiredMixin, TemplateView):
    template_name = 'portal/data.html'
    allowed_groups = ['pl:data', 'pl:admin', 'admin:data']


class EditorView(GroupRequiredMixin, TemplateView):
    template_name = 'portal/editor.html'
    allowed_groups = ['pl:editor', 'pl:admin']


class PoliciesAdminView(GroupRequiredMixin, TemplateView):
    template_name = 'portal/admin_section.html'
    allowed_groups = ['pl:admin']
