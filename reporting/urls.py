from django.urls import path
from .views import *
from rms.page_info_collection import PageInfoCollection

urlpatterns = [
    ################################################################
    #   Avaya CDR
    ################################################################
    path(
        "viewAvayaCDR/",
        viewAvayaCDR,
        name=PageInfoCollection.AVAYACDR_VIEW.urlName,
    ),
    # path(
    #     "createShiftLegend",
    #     createShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_CREATE.urlName,
    # ),
    # path(
    #     "editShiftLegend/<int:id>/",
    #     editShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_EDIT.urlName,
    # ),
    # path(
    #     "viewShiftLegendListJson/",
    #     viewShiftLegendListJson.as_view(),
    #     name=PageInfoCollection.SHIFTLEGEND_JSON.urlName,
    # ),
    # path(
    #     "deleteShiftLegend/<int:id>/",
    #     deleteShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_DELETE.urlName,
    # ),
    path(
        "createBulkAvayaCDR",
        createBulkAvayaCDR,
        name=PageInfoCollection.AVAYACDR_BULK.urlName,
    ),
    ################################################################
    #   Agent Hourly Performance
    ################################################################
    path(
        "viewAgentHourlyPerformance/",
        viewAgentHourlyPerformance,
        name=PageInfoCollection.AGENTHOURLYPERFORMANCE_VIEW.urlName,
    ),
    # path(
    #     "createShiftLegend",
    #     createShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_CREATE.urlName,
    # ),
    # path(
    #     "editShiftLegend/<int:id>/",
    #     editShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_EDIT.urlName,
    # ),
    # path(
    #     "viewShiftLegendListJson/",
    #     viewShiftLegendListJson.as_view(),
    #     name=PageInfoCollection.SHIFTLEGEND_JSON.urlName,
    # ),
    # path(
    #     "deleteShiftLegend/<int:id>/",
    #     deleteShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_DELETE.urlName,
    # ),
    path(
        "createBulkAgentHourlyPerformance",
        createBulkAgentHourlyPerformance,
        name=PageInfoCollection.AGENTHOURLYPERFORMANCE_BULK.urlName,
    ),
    ################################################################
    #   Login Logout Time
    ################################################################
    path(
        "viewLoginLogoutTime/",
        viewLoginLogoutTime,
        name=PageInfoCollection.LOGINLOGOUTTIME_VIEW.urlName,
    ),
    # path(
    #     "createShiftLegend",
    #     createShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_CREATE.urlName,
    # ),
    # path(
    #     "editShiftLegend/<int:id>/",
    #     editShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_EDIT.urlName,
    # ),
    # path(
    #     "viewShiftLegendListJson/",
    #     viewShiftLegendListJson.as_view(),
    #     name=PageInfoCollection.SHIFTLEGEND_JSON.urlName,
    # ),
    # path(
    #     "deleteShiftLegend/<int:id>/",
    #     deleteShiftLegend,
    #     name=PageInfoCollection.SHIFTLEGEND_DELETE.urlName,
    # ),
    path(
        "createBulkLoginLogoutTime",
        createBulkLoginLogoutTime,
        name=PageInfoCollection.LOGINLOGOUTTIME_BULK.urlName,
    ),
    ################################################################
    #   Reporting One
    ################################################################
    path(
        "viewReportingOne/",
        viewReportingOne,
        name=PageInfoCollection.REPORTINGONE_VIEW.urlName,
    ),
    path(
        "viewReportingOneListJson/",
        viewReportingOneListJson.as_view(),
        name=PageInfoCollection.REPORTINGONE_JSON.urlName,
    ),
    ################################################################
    #   Reporting Two
    ################################################################
    path(
        "viewReportingTwo/",
        viewReportingTwo,
        name=PageInfoCollection.REPORTINGTWO_VIEW.urlName,
    ),
    path(
        "viewReportingTwoListJson/",
        viewReportingTwoListJson.as_view(),
        name=PageInfoCollection.REPORTINGTWO_JSON.urlName,
    ),
    ################################################################
    #   Reporting Three
    ################################################################
    path(
        "viewReportingThree/",
        viewReportingThree,
        name=PageInfoCollection.REPORTINGTHREE_VIEW.urlName,
    ),
    path(
        "viewReportingThreeListJson/",
        viewReportingThreeListJson.as_view(),
        name=PageInfoCollection.REPORTINGTHREE_JSON.urlName,
    ),
]
