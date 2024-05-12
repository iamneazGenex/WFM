from django import forms
from .models import *


class AvayaCDRForm(forms.ModelForm):
    class Meta:
        model = AvayaCDR
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Additional save logic can be added here
        if commit:
            instance.save()

        return instance
