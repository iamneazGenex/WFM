from django import forms
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe


class EmployeeSelectWidget(forms.Select):
    template_name = "widgets/employee_select_widget.html"

    class Media:
        css = {"all": ("path/to/your/css/employee_select_widget.css",)}
        js = ("path/to/your/js/employee_select_widget.js",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["employee_select_url"] = reverse_lazy("employee_select_list")
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return render_to_string(self.template_name, context)
