from . import views
from django.urls import path
from rms.page_info_collection import PageInfo, PageInfoCollection

urlpatterns = [
    ################################################################
    #   Day Off Trading
    ################################################################
    path(
        "day_off_trading_requests",
        views.viewDayOffTradingRequests,
        name=PageInfoCollection.DAYOFFTRADING_VIEW.urlName,
    ),
    path(
        "create_day_off_trading_request",
        views.createDayOffTrading,
        name=PageInfoCollection.DAYOFFTRADING_CREATE.urlName,
    ),
    path(
        "day_off_trading_list_json/",
        views.DayOffTradingListJson.as_view(),
        name=PageInfoCollection.DAYOFFTRADING_JSON.urlName,
    ),
    path(
        "acceptDayOffTrading/<int:id>/",
        views.acceptDayOffTrading,
        name="accept_day_off_trading",
    ),
    path(
        "rejectDayOffTrading/<int:id>/",
        views.rejectDayOffTrading,
        name="reject_day_off_trading",
    ),
    ################################################################
    #   Shift Time Trading
    ################################################################
    path(
        "shiftTimeTrading",
        views.createshiftTimeTrading,
        name=PageInfoCollection.SHIFTTIMETRADING_CREATE.urlName,
    ),
    path(
        "viewShiftTimeTradingRequests",
        views.viewShiftTimeTradingRequests,
        name=PageInfoCollection.SHIFTTIMETRADING_VIEW.urlName,
    ),
    path(
        "acceptShiftTimeTrading/<int:id>/",
        views.acceptShiftTimeTrading,
        name="accept_shift_time_trading",
    ),
    path(
        "rejectShiftTimeTrading/<int:id>/",
        views.rejectShiftTimeTrading,
        name="reject_shift_time_trading",
    ),
    path(
        "shift-time-trading-list-json/",
        views.ShiftTimeTradingListJson.as_view(),
        name="shift_time_trading_list_json",
    ),
    path(
        "test/",
        views.test,
        name="test",
    ),
    path("get_roster_details/", views.get_roster_details, name="get_roster_details"),
]
