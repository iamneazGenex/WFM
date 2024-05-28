from django.contrib.auth import views
from django.urls import path, include
from .views import *
from .utils import *
from rms.page_info_collection import PageInfoCollection
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView

urlpatterns = [
    # path("login/", views.LoginView.as_view(), name="login"),
    # path("logout/", views.LogoutView.as_view(), name="logout"),
    path("", home, name="home"),
    path(
        "password_change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path("", include("django.contrib.auth.urls")),
    path("viewSettings/", viewSettings, name=PageInfoCollection.SETTINGS.urlName),
    path("viewUsers/", viewUsers, name=PageInfoCollection.USERS.urlName),
    path("createEmployee/", createEmployee, name="createEmployee"),
    path("bulkAddEmployees/", bulkAddEmployees, name="bulkAddEmployees"),
    ################################################################
    #   Process
    ################################################################
    path("viewProcess/", viewProcess, name=PageInfoCollection.PROCESS_VIEW.urlName),
    path(
        "viewProcessJson/",
        viewProcessJson.as_view(),
        name=PageInfoCollection.PROCESS_JSON.urlName,
    ),
    path(
        "deleteProcess/<int:id>/",
        deleteProcess,
        name=PageInfoCollection.PROCESS_DELETE.urlName,
    ),
    path(
        "createProcess/", createProcess, name=PageInfoCollection.PROCESS_CREATE.urlName
    ),
    path(
        "editProcess/<int:id>/",
        editProcess,
        name=PageInfoCollection.PROCESS_EDIT.urlName,
    ),
    ################################################################
    #   Site
    ################################################################
    path("createSite/", createSite, name=PageInfoCollection.SITE_CREATE.urlName),
    path("viewSite/", viewSite, name=PageInfoCollection.SITE_VIEW.urlName),
    path(
        "viewSiteJson/",
        viewSiteJson.as_view(),
        name=PageInfoCollection.SITE_JSON.urlName,
    ),
    path("editSite/<int:id>/", editSite, name=PageInfoCollection.SITE_EDIT.urlName),
    path(
        "deleteSite/<int:id>/",
        deleteSite,
        name=PageInfoCollection.SITE_DELETE.urlName,
    ),
    ################################################################
    #   LOB
    ################################################################
    path("createLOB/", createLOB, name=PageInfoCollection.LOB_CREATE.urlName),
    path("viewLOB/", viewLOB, name=PageInfoCollection.LOB_VIEW.urlName),
    path(
        "viewLOBJson/", viewLOBJson.as_view(), name=PageInfoCollection.LOB_JSON.urlName
    ),
    path("editLOB/<int:id>/", editLOB, name=PageInfoCollection.LOB_EDIT.urlName),
    path(
        "deleteLOB/<int:id>/",
        deleteLOB,
        name=PageInfoCollection.LOB_DELETE.urlName,
    ),
    ################################################################
    #   WorkRole
    ################################################################
    path(
        "createWorkRole/",
        createWorkRole,
        name=PageInfoCollection.WORKROLE_CREATE.urlName,
    ),
    path("viewWorkRole/", viewWorkRole, name=PageInfoCollection.WORKROLE_VIEW.urlName),
    path(
        "viewWorkRoleJson/",
        viewWorkRoleJson.as_view(),
        name=PageInfoCollection.WORKROLE_JSON.urlName,
    ),
    path(
        "editWorkRole/<int:id>/",
        editWorkRole,
        name=PageInfoCollection.WORKROLE_EDIT.urlName,
    ),
    path(
        "deleteWorkRole/<int:id>/",
        deleteWorkRole,
        name=PageInfoCollection.WORKROLE_DELETE.urlName,
    ),
    ################################################################
    #   Skill
    ################################################################
    path(
        "createSkill/",
        createSkill,
        name=PageInfoCollection.SKILL_CREATE.urlName,
    ),
    path("viewSkill/", viewSkill, name=PageInfoCollection.SKILL_VIEW.urlName),
    path(
        "viewSkillJson/",
        viewSkillJson.as_view(),
        name=PageInfoCollection.SKILL_JSON.urlName,
    ),
    path(
        "editSkill/<int:id>/",
        editSkill,
        name=PageInfoCollection.SKILL_EDIT.urlName,
    ),
    path(
        "deleteSkill/<int:id>/",
        deleteSkill,
        name=PageInfoCollection.SKILL_DELETE.urlName,
    ),
    ################################################################
    #   Supervisor
    ################################################################
    path(
        "createSupervisor/",
        createSupervisor,
        name=PageInfoCollection.SUPERVISOR_CREATE.urlName,
    ),
    path(
        "editSupervisor/<int:id>/",
        editSupervisor,
        name=PageInfoCollection.SUPERVISOR_EDIT.urlName,
    ),
    path(
        "bulkAddSupervisors/",
        bulkAddSupervisors,
        name=PageInfoCollection.SUPERVISOR_BULK.urlName,
    ),
    path(
        "viewSupervisor/",
        viewSupervisor,
        name=PageInfoCollection.SUPERVISOR_VIEW.urlName,
    ),
    path(
        "viewSupervisorJson/",
        ViewSupervisorJson.as_view(),
        name=PageInfoCollection.SUPERVISOR_JSON.urlName,
    ),
    path(
        "deleteSupervisor/<int:id>/",
        deleteSupervisor,
        name=PageInfoCollection.SUPERVISOR_DELETE.urlName,
    ),
    ################################################################
    #   Employee
    ################################################################
    path(
        "createEmployee/",
        createEmployee,
        name=PageInfoCollection.EMPLOYEE_CREATE.urlName,
    ),
    path(
        "editEmployee/<int:id>/",
        editEmployee,
        name=PageInfoCollection.EMPLOYEE_EDIT.urlName,
    ),
    path(
        "bulkAddEmployees/",
        bulkAddEmployees,
        name=PageInfoCollection.EMPLOYEE_BULK.urlName,
    ),
    path("viewEmployee/", viewEmployee, name=PageInfoCollection.EMPLOYEE_VIEW.urlName),
    path(
        "viewEmployeeJson/",
        ViewEmployeeJson.as_view(),
        name=PageInfoCollection.EMPLOYEE_JSON.urlName,
    ),
    path(
        "deleteEmployee/<int:id>/",
        deleteEmployee,
        name=PageInfoCollection.EMPLOYEE_DELETE.urlName,
    ),
    path(
        "bulkAddEmployeesOtherInfo/",
        bulkAddEmployeesOtherInfo,
        name=PageInfoCollection.EMPLOYEE_OTHERINFO.urlName,
    ),
    ################################################################
    #   Group
    ################################################################
    path(
        "createGroup/",
        createGroup,
        name=PageInfoCollection.GROUP_CREATE.urlName,
    ),
    path("viewGroup/", viewGroup, name=PageInfoCollection.GROUP_VIEW.urlName),
    path(
        "viewGroupJson/",
        viewGroupJson.as_view(),
        name=PageInfoCollection.GROUP_JSON.urlName,
    ),
    path(
        "editGroup/<int:id>/",
        editGroup,
        name=PageInfoCollection.GROUP_EDIT.urlName,
    ),
    path(
        "deleteGroup/<int:id>/",
        deleteGroup,
        name=PageInfoCollection.GROUP_DELETE.urlName,
    ),
    ################################################################
    #   User
    ################################################################
    path(
        "createUser/",
        createUser,
        name=PageInfoCollection.USER_CREATE.urlName,
    ),
    path("viewUser/", viewUser, name=PageInfoCollection.USER_VIEW.urlName),
    path(
        "viewUserJson/",
        viewUserJson.as_view(),
        name=PageInfoCollection.USER_JSON.urlName,
    ),
    path(
        "editUser/<int:id>/",
        editUser,
        name=PageInfoCollection.USER_EDIT.urlName,
    ),
    path(
        "deleteUser/<int:id>/",
        deleteUser,
        name=PageInfoCollection.USER_DELETE.urlName,
    ),
]
