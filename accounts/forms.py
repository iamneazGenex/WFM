from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from django import forms
from django.contrib.auth.models import Group


class CustomUserCreationForm(UserChangeForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = "__all__"


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


# class CreateSupervisorForm(forms.Form):
#     # Fields from UserCreationForm
#     email = forms.EmailField(max_length=254)
#     name = forms.CharField(max_length=255)
#     password = forms.CharField(label="Password", widget=forms.PasswordInput)
#     password_confirm = forms.CharField(
#         label="Password confirmation", widget=forms.PasswordInput
#     )
#     # Fields from Supervisor model
#     employee_id = forms.IntegerField(label="Employee ID", required=True)
#     system_id = forms.IntegerField(label="System ID", required=True)
#     process = forms.ModelChoiceField(
#         label="Process", queryset=Process.objects.all(), required=True
#     )
#     gender = forms.ChoiceField(
#         label="Gender", choices=Supervisor.GENDER_CHOICES, required=False
#     )
#     site = forms.ModelChoiceField(
#         label="Site", queryset=Site.objects.all(), required=False
#     )
#     work_role = forms.ModelChoiceField(
#         label="Work Role", queryset=WorkRole.objects.all(), required=False
#     )

#     def __init__(self, *args, **kwargs):
#         super(CreateSupervisorForm, self).__init__(*args, **kwargs)
#         self.fields["process"].choices = [(None, "--------")] + [
#             (process.id, process.name.capitalize()) for process in Process.objects.all()
#         ]
#         self.fields["site"].choices = [(None, "--------")] + [
#             (site.id, site.name.capitalize()) for site in Site.objects.all()
#         ]
#         self.fields["work_role"].choices = [(None, "--------")] + [
#             (role.id, role.name.capitalize()) for role in WorkRole.objects.all()
#         ]

#     def clean(self):
#         cd = self.cleaned_data
#         if cd.get("password") != cd.get("password_confirm"):
#             self.add_error("password_confirm", "passwords do not match !")
#         return cd


class CustomUserForm(UserCreationForm):
    employee_id = forms.IntegerField(label="Employee ID", required=True)
    system_id = forms.IntegerField(label="System ID", required=True)

    class Meta:
        model = CustomUser
        fields = ["email", "name", "password1", "password2", "employee_id", "system_id"]


class SupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = [
            "process",
            "gender",
            "site",
            "work_role",
        ]

    def __init__(self, *args, **kwargs):
        super(SupervisorForm, self).__init__(*args, **kwargs)
        self.fields["process"].queryset = Process.objects.all()
        self.fields["site"].queryset = Site.objects.all()
        self.fields["work_role"].queryset = WorkRole.objects.all()


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "process",
            "gender",
            "site",
            "work_role",
            "lob",
            "pick_drop_location",
            "supervisor_1",
            "supervisor_2",
        ]

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields["process"].queryset = Process.objects.all()
        self.fields["site"].queryset = Site.objects.all()
        self.fields["work_role"].queryset = WorkRole.objects.all()
        self.fields["lob"].queryset = LOB.objects.all()
        self.fields["supervisor_1"].queryset = Employee.objects.all()
        self.fields["supervisor_2"].queryset = Employee.objects.all()


class CreateEditSupervisorForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput, required=False
    )

    # Manually set choices for process, site, and work_role
    process = forms.ModelChoiceField(queryset=Process.objects.all())
    site = forms.ModelChoiceField(queryset=Site.objects.all())
    work_role = forms.ModelChoiceField(queryset=WorkRole.objects.all())

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "name",
            "employee_id",
            "system_id",
        ]

    def __init__(self, *args, **kwargs):
        super(CreateEditSupervisorForm, self).__init__(*args, **kwargs)

        # Create an instance of SupervisorForm
        supervisor_form = SupervisorForm(*args, **kwargs)

        # Update fields with SupervisorForm fields
        self.fields.update(supervisor_form.fields)

        # Capitalize the items for process, site, and work_role
        self.fields["process"].widget.choices = [
            (value, label.capitalize())
            for value, label in supervisor_form.fields["process"].widget.choices
        ]
        self.fields["site"].widget.choices = [
            (value, label.capitalize())
            for value, label in supervisor_form.fields["site"].widget.choices
        ]
        self.fields["work_role"].widget.choices = [
            (value, label.capitalize())
            for value, label in supervisor_form.fields["work_role"].widget.choices
        ]
        # Determine if this is an edit operation
        is_editing = self.instance.pk is not None
        # Hide password fields if editing an existing supervisor
        if is_editing:
            supervisor_data = self.instance.__dict__
            self.initial.update(supervisor_data)

            custom_user_data = self.instance.user.__dict__
            self.initial.update(custom_user_data)

            self.fields["process"].choices = [
                (process.id, process.name.capitalize())
                for process in Process.objects.all()
            ]
            self.fields["site"].choices = [
                (site.id, site.name.capitalize()) for site in Site.objects.all()
            ]
            self.fields["work_role"].choices = [
                (role.id, role.name.capitalize()) for role in WorkRole.objects.all()
            ]

            self.fields["process"].initial = self.instance.process
            self.fields["gender"].initial = self.instance.gender
            self.fields["site"].initial = self.instance.site
            self.fields["work_role"].initial = self.instance.work_role

            self.fields["password1"].widget.attrs["style"] = "display:none;"
            self.fields["password2"].widget.attrs["style"] = "display:none;"
            self.fields["password1"].label = ""
            self.fields["password2"].label = ""

    def clean(self):
        cd = super().clean()

        # Check password only during creation
        if not self.instance.pk:
            password1 = cd.get("password1")
            password2 = cd.get("password2")

            if password1 != password2:
                self.add_error("password2", "Passwords do not match!")

        return cd


class CreateEditEmployeeForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput, required=False
    )

    # Manually set choices for process, site, and work_role
    process = forms.ModelChoiceField(queryset=Process.objects.all())
    site = forms.ModelChoiceField(queryset=Site.objects.all())
    work_role = forms.ModelChoiceField(queryset=WorkRole.objects.all())

    class Meta:
        model = CustomUser
        fields = [
            "is_active",
            "email",
            "name",
            "employee_id",
            "system_id",
        ]

    def __init__(self, *args, **kwargs):
        super(CreateEditEmployeeForm, self).__init__(*args, **kwargs)

        # Create an instance of EmployeeForm
        employee_form = EmployeeForm(*args, **kwargs)

        # Update fields with EmployeeForm fields
        self.fields.update(employee_form.fields)

        # Capitalize the items for process, site, and work_role
        self.fields["process"].widget.choices = [
            (value, label.capitalize())
            for value, label in employee_form.fields["process"].widget.choices
        ]
        self.fields["site"].widget.choices = [
            (value, label.capitalize())
            for value, label in employee_form.fields["site"].widget.choices
        ]
        self.fields["work_role"].widget.choices = [
            (value, label.capitalize())
            for value, label in employee_form.fields["work_role"].widget.choices
        ]
        self.fields["lob"].widget.choices = [
            (value, label.capitalize())
            for value, label in employee_form.fields["lob"].widget.choices
        ]
        self.fields["supervisor_1"].queryset = Employee.objects.exclude(
            id=self.instance.id
        )
        self.fields["supervisor_2"].queryset = Employee.objects.exclude(
            id=self.instance.id
        )
        self.fields["is_active"].initial = True
        # Determine if this is an edit operation
        is_editing = self.instance.pk is not None
        # Hide password fields if editing an existing supervisor
        if is_editing:
            employee_data = self.instance.__dict__
            self.initial.update(employee_data)

            custom_user_data = self.instance.user.__dict__
            self.initial.update(custom_user_data)

            self.fields["process"].initial = self.instance.process
            self.fields["gender"].initial = self.instance.gender
            self.fields["site"].initial = self.instance.site
            self.fields["work_role"].initial = self.instance.work_role
            self.fields["lob"].initial = self.instance.lob
            self.fields["supervisor_1"].initial = self.instance.supervisor_1
            self.fields["supervisor_2"].initial = self.instance.supervisor_2

            self.fields["password1"].widget.attrs["style"] = "display:none;"
            self.fields["password2"].widget.attrs["style"] = "display:none;"
            self.fields["password1"].label = ""
            self.fields["password2"].label = ""

            # Initialize is_active field for editing
            self.fields["is_active"].initial = custom_user_data["is_active"]

    def clean(self):
        cd = super().clean()

        # Check password only during creation
        if not self.instance.pk:
            password1 = cd.get("password1")
            password2 = cd.get("password2")

            if password1 != password2:
                self.add_error("password2", "Passwords do not match!")
        # Check if supervisor_1 and supervisor_2 are the same as the employee
        supervisor_1 = cd.get("supervisor_1")
        supervisor_2 = cd.get("supervisor_2")

        if supervisor_1 and supervisor_2 and supervisor_1 == supervisor_2:
            self.add_error(
                "supervisor_2", "Supervisor 2 cannot be the same as Supervisor 1."
            )

        return cd


class CreateEmployeeForm(forms.Form):
    # Fields from UserCreationForm
    email = forms.EmailField(max_length=254)
    name = forms.CharField(max_length=255)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password_confirm = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )
    # Fields from Employee model
    employee_id = forms.IntegerField(label="Employee ID", required=True)
    system_id = forms.IntegerField(label="System ID", required=True)
    process = forms.ModelChoiceField(
        label="Process", queryset=Process.objects.all(), required=True
    )
    gender = forms.ChoiceField(
        label="Gender", choices=Supervisor.GENDER_CHOICES, required=False
    )
    site = forms.ModelChoiceField(
        label="Site", queryset=Site.objects.all(), required=False
    )
    work_role = forms.ModelChoiceField(
        label="Work Role", queryset=WorkRole.objects.all(), required=False
    )
    lob = forms.ModelChoiceField(
        label="LOB", queryset=LOB.objects.all(), required=False
    )
    pick_drop_location = forms.CharField(max_length=255)
    supervisor_1 = forms.ModelChoiceField(
        label="Supervisor 1", queryset=Supervisor.objects.all(), required=True
    )
    supervisor_2 = forms.ModelChoiceField(
        label="Supervisor 2", queryset=Supervisor.objects.all(), required=False
    )

    def clean(self):
        cd = self.cleaned_data
        if cd.get("password") != cd.get("password_confirm"):
            self.add_error("password_confirm", "passwords do not match !")
        return cd


class CreateProcess(forms.ModelForm):
    name = forms.CharField(max_length=255, label="Name", required=True)

    class Meta:
        model = Process
        fields = ["name"]
        labels = {"name": "Name"}


class CreateSite(forms.ModelForm):
    name = forms.CharField(max_length=255, label="Name", required=True)

    class Meta:
        model = Site
        fields = ["name"]
        labels = {"name": "Name"}


class CreateLOB(forms.ModelForm):
    name = forms.CharField(max_length=255, label="Name", required=True)

    class Meta:
        model = LOB
        fields = ["name"]
        labels = {"name": "Name"}


class CreateWorkRole(forms.ModelForm):
    name = forms.CharField(max_length=255, label="Name", required=True)

    class Meta:
        model = WorkRole
        fields = ["name"]
        labels = {"name": "Name"}


class CreateSkill(forms.ModelForm):
    name = forms.CharField(max_length=255, label="Name", required=True)

    class Meta:
        model = Skill
        fields = ["name"]
        labels = {"name": "Name"}


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}
