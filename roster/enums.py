class PageInfo:
    def __init__(self, pageName, urlName):
        self.pageName = pageName
        self.urlName = urlName


class PageInfoEnum:
    SETTINGS = PageInfo("Settings", "viewSettings")
    USERS = PageInfo("Settings", "viewUsers")
    ################################################################
    #   Process
    ################################################################
    PROCESS_VIEW = PageInfo("Process", "viewProcess")
    PROCESS_CREATE = PageInfo("Create", "createProcess")
    PROCESS_EDIT = PageInfo("Edit", "editProcess")
    PROCESS_DELETE = PageInfo("Delete", "deleteProcess")
    PROCESS_JSON = PageInfo("JSON", "viewProcessJson")
    ################################################################
    #   Site
    ################################################################
    SITE_VIEW = PageInfo("Site", "viewSite")
    SITE_CREATE = PageInfo("Create", "createSite")
    SITE_EDIT = PageInfo("Edit", "editSite")
    SITE_DELETE = PageInfo("Delete", "deleteSite")
    SITE_JSON = PageInfo("JSON", "viewSiteJson")
    ################################################################
    #   LOB
    ################################################################
    LOB_VIEW = PageInfo("LOB", "viewLOB")
    LOB_CREATE = PageInfo("Create", "createLOB")
    LOB_EDIT = PageInfo("Edit", "editLOB")
    LOB_DELETE = PageInfo("Delete", "deleteLOB")
    LOB_JSON = PageInfo("JSON", "viewLOBJson")
    ################################################################
    #   WorkRole
    ################################################################
    WORKROLE_VIEW = PageInfo("Work Role", "viewWorkRole")
    WORKROLE_CREATE = PageInfo("Create", "createWorkRole")
    WORKROLE_EDIT = PageInfo("Edit", "editWorkRole")
    WORKROLE_DELETE = PageInfo("Delete", "deleteWorkRole")
    WORKROLE_JSON = PageInfo("JSON", "viewWorkRoleJson")
    ################################################################
    #   SUPERVISOR
    ################################################################
    SUPERVISOR_VIEW = PageInfo("Supervisor", "viewSupervisor")
    SUPERVISOR_CREATE = PageInfo("Create", "createSupervisor")
    SUPERVISOR_EDIT = PageInfo("Edit", "editSupervisor")
    SUPERVISOR_DELETE = PageInfo("Delete", "deleteSupervisor")
    SUPERVISOR_JSON = PageInfo("JSON", "viewSupervisorJson")
    SUPERVISOR_BULK = PageInfo("Bulk", "viewSupervisorBulk")
    ################################################################
    #   EMPLOYEE
    ################################################################
    EMPLOYEE_VIEW = PageInfo("Employee", "viewEmployee")
    EMPLOYEE_CREATE = PageInfo("Create", "createEmployee")
    EMPLOYEE_EDIT = PageInfo("Edit", "editEmployee")
    EMPLOYEE_DELETE = PageInfo("Delete", "deleteWorkRole")
    EMPLOYEE_JSON = PageInfo("JSON", "viewEmployeeJson")
    EMPLOYEE_BULK = PageInfo("Bulk", "viewEmployeeBulk")
    ################################################################
    #   WORKRULE
    ################################################################
    WORKRULE_VIEW = PageInfo("WORKRULE", "viewWorkRule")
    WORKRULE_EDIT = PageInfo("Edit", "editWorkRule")
    WORKRULE_JSON = PageInfo("JSON", "viewWorkRuleJson")
