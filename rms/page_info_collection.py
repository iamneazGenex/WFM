class PageInfo:
    def __init__(self, pageName, urlName):
        self.pageName = pageName
        self.urlName = urlName


class PageInfoCollection:
    SETTINGS = PageInfo("Settings", "viewSettings")
    USERS = PageInfo("Users", "viewUsers")
    ROSTERMANAGEMENT = PageInfo("Roster Management", "viewRosterManagement")
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
    #   Skill
    ################################################################
    SKILL_VIEW = PageInfo("Skill", "viewSkill")
    SKILL_CREATE = PageInfo("Create", "createSkill")
    SKILL_EDIT = PageInfo("Edit", "editSkill")
    SKILL_DELETE = PageInfo("Delete", "deleteSkill")
    SKILL_JSON = PageInfo("JSON", "viewSkillJson")
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
    EMPLOYEE_DELETE = PageInfo("Delete", "deleteEmployee")
    EMPLOYEE_JSON = PageInfo("JSON", "viewEmployeeJson")
    EMPLOYEE_BULK = PageInfo("Bulk", "viewEmployeeBulk")
    EMPLOYEE_OTHERINFO = PageInfo("Other Info", "viewEmployeeOtherInfo")
    ################################################################
    #   WORKRULE
    ################################################################
    WORKRULE_CREATE = PageInfo("Create", "createWorkRule")
    WORKRULE_VIEW = PageInfo("WORKRULE", "viewWorkRule")
    WORKRULE_EDIT = PageInfo("Edit", "editWorkRule")
    WORKRULE_JSON = PageInfo("JSON", "viewWorkRuleJson")
    ################################################################
    #   Roster
    ################################################################
    ROSTER_VIEW = PageInfo("Roster", "viewRoster")
    ROSTER_CREATE = PageInfo("Create", "createRoster")
    ROSTER_EDIT = PageInfo("Edit", "editRoster")
    ROSTER_DELETE = PageInfo("Delete", "deleteRoster")
    ROSTER_JSON = PageInfo("JSON", "viewRosterJson")
    ROSTER_BULK = PageInfo("Bulk", "viewRosterBulk")
    ################################################################
    #   Roster Count
    ################################################################
    ROSTERCOUNT_VIEW = PageInfo("Roster Count", "viewRosterCount")
    ROSTERCOUNT_JSON = PageInfo("JSON", "viewRosterCountJson")
    ################################################################
    #   Roster Seat Count
    ################################################################
    ROSTERSEATCOUNT_VIEW = PageInfo("Roster Seat Count", "viewRosterSeatCount")
    ROSTERSEATCOUNT_JSON = PageInfo("JSON", "viewRosterSeatCountJson")
    ROSTERSEATCOUNT_CREATE = PageInfo("Create", "createRosterSeatCount")
    ROSTERSEATCOUNT_EDIT = PageInfo("Edit", "editRosterSeatCount")
    ROSTERSEATCOUNT_DELETE = PageInfo("Delete", "deleteRosterSeatCount")
    ROSTERSEATCOUNT_BULK = PageInfo("Bulk", "viewRosterSeatCountBulk")

    ################################################################
    #   Day Off Trading
    ################################################################
    DAYOFFTRADING_VIEW = PageInfo("Day Off Trading", "viewDayOffTradingRequests")
    DAYOFFTRADING_JSON = PageInfo("JSON", "viewDayoffTradingListJson")
    DAYOFFTRADING_CREATE = PageInfo("Create", "createDayOffTradingRequests")
    DAYOFFTRADING_EDIT = PageInfo("Edit", "viewDayOffTradingRequests")
    DAYOFFTRADING_DELETE = PageInfo("Delete", "viewDayOffTradingRequests")
    DAYOFFTRADING_BULK = PageInfo("Bulk", "viewDayOffTradingRequests")

    ################################################################
    #   Shift Time Trading
    ################################################################
    SHIFTTIMETRADING_VIEW = PageInfo(
        "Shift Time Trading", "viewShiftTimeTradingRequests"
    )
    SHIFTTIMETRADING_JSON = PageInfo("JSON", "shift_time_trading_list_json")
    SHIFTTIMETRADING_CREATE = PageInfo("Create", "shiftTimeTrading")
    SHIFTTIMETRADING_EDIT = PageInfo("Edit", "viewDayOffTradingRequests")
    SHIFTTIMETRADING_DELETE = PageInfo("Delete", "viewDayOffTradingRequests")
    SHIFTTIMETRADING_BULK = PageInfo("Bulk", "viewDayOffTradingRequests")

    ################################################################
    #   Forecasting
    ################################################################
    FORECASTING_VIEW = PageInfo("Forecasting", "viewForecasting")
    FORECASTING_JSON = PageInfo("JSON", "viewForecastingListJson")
    FORECASTING_CREATE = PageInfo("Create", "createForecasting")
    FORECASTING_EDIT = PageInfo("Edit", "editForecasting")
    FORECASTING_DELETE = PageInfo("Delete", "deleteForecasting")
    FORECASTING_BULK = PageInfo("Bulk", "createBulkForecasting")

    ################################################################
    #   Shift Legend
    ################################################################
    SHIFTLEGEND_VIEW = PageInfo("Shift Legend", "viewShiftLegend")
    SHIFTLEGEND_JSON = PageInfo("JSON", "viewShiftLegendListJson")
    SHIFTLEGEND_CREATE = PageInfo("Create", "createShiftLegend")
    SHIFTLEGEND_EDIT = PageInfo("Edit", "editShiftLegend")
    SHIFTLEGEND_DELETE = PageInfo("Delete", "deleteShiftLegend")
    SHIFTLEGEND_BULK = PageInfo("Bulk", "createBulkShiftLegend")
    ################################################################
    #   Avaya CDR
    ################################################################
    AVAYACDR_VIEW = PageInfo("Avaya CDR", "viewAvayaCDR")
    AVAYACDR_JSON = PageInfo("JSON", "viewAvayaCDRListJson")
    AVAYACDR_CREATE = PageInfo("Create", "createAvayaCDR")
    AVAYACDR_EDIT = PageInfo("Edit", "editAvayaCDR")
    AVAYACDR_DELETE = PageInfo("Delete", "deleteAvayaCDR")
    AVAYACDR_BULK = PageInfo("Bulk", "createBulkAvayaCDR")
    ################################################################
    #   Agent Hourly Performance
    ################################################################
    AGENTHOURLYPERFORMANCE_VIEW = PageInfo(
        "Agent Hourly Performance", "viewAgentHourlyPerformance"
    )
    AGENTHOURLYPERFORMANCE_JSON = PageInfo("JSON", "viewAgentHourlyPerformanceListJson")
    AGENTHOURLYPERFORMANCE_CREATE = PageInfo("Create", "createAgentHourlyPerformance")
    AGENTHOURLYPERFORMANCE_EDIT = PageInfo("Edit", "editAgentHourlyPerformance")
    AGENTHOURLYPERFORMANCE_DELETE = PageInfo("Delete", "deleteAgentHourlyPerformance")
    AGENTHOURLYPERFORMANCE_BULK = PageInfo("Bulk", "createBulkAgentHourlyPerformance")
    ################################################################
    #   Login Logout Time
    ################################################################
    LOGINLOGOUTTIME_VIEW = PageInfo("Login Logout Time", "viewLoginLogoutTime")
    LOGINLOGOUTTIME_JSON = PageInfo("JSON", "viewLoginLogoutTimeListJson")
    LOGINLOGOUTTIME_CREATE = PageInfo("Create", "createLoginLogoutTime")
    LOGINLOGOUTTIME_EDIT = PageInfo("Edit", "editLoginLogoutTime")
    LOGINLOGOUTTIME_DELETE = PageInfo("Delete", "deleteLoginLogoutTime")
    LOGINLOGOUTTIME_BULK = PageInfo("Bulk", "createBulkLoginLogoutTime")
    ################################################################
    #   Reporting One
    ################################################################
    REPORTINGONE_VIEW = PageInfo("Forecast & Plan Vs Actual Report", "viewReportingOne")
    REPORTINGONE_JSON = PageInfo("JSON", "viewReportingOneListJson")
    ################################################################
    #   Reporting Two
    ################################################################
    REPORTINGTWO_VIEW = PageInfo("Staffed Report", "viewReportingTwo")
    REPORTINGTWO_JSON = PageInfo("JSON", "viewReportingTwoListJson")
    ################################################################
    #   Reporting Three
    ################################################################
    REPORTINGTHREE_VIEW = PageInfo("Agent Staffed Report", "viewReportingThree")
    REPORTINGTHREE_JSON = PageInfo("JSON", "viewReportingThreeListJson")
    ################################################################
    #   Group
    ################################################################
    GROUP_VIEW = PageInfo("Group", "viewGroup")
    GROUP_CREATE = PageInfo("Create", "createGroup")
    GROUP_EDIT = PageInfo("Edit", "editGroup")
    GROUP_DELETE = PageInfo("Delete", "deleteGroup")
    GROUP_JSON = PageInfo("JSON", "viewGroupJson")
