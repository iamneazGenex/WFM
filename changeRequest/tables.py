import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from .models import *
from django.utils.html import format_html
from django_tables2.utils import Accessor


class DayOffTradingTableEmployee(tables.Table):
    # Your existing columns go here
    requestor = tables.Column(verbose_name="Requestor", attrs={"width": "20%"})
    requestee_swap_roster = tables.Column(
        verbose_name="Swap Date",
        accessor=Accessor("requestee_swap_roster"),
        orderable=True,
    )
    requestee_trade_roster = tables.Column(
        verbose_name="Trade Date",
        accessor=Accessor("requestee_trade_roster"),
        orderable=True,
    )
    created_At = tables.Column(verbose_name="Requested At", orderable=True)
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)

    # Define a custom column for "Accept" and "Reject" buttons
    class Meta:
        model = DayOffTrading
        ordering = "-created_At"
        sequence = (
            "requestor",
            "requestee_swap_roster",
            "requestee_trade_roster",
        )
        exclude = (
            "id",
            "requestee",
            "requestor_swap_roster",
            "requestor_trade_roster",
            "requestee_approval_status",
            "requestee_approval_status_datetime",
            "supervisor",
            "supervisor_approval_status",
            "supervisor_approval_status_datetime",
            "updated_At",
        )
        row_attrs = {"data-id": lambda record: record.id}
        attrs = {
            "th": {
                "_ordering": {
                    "orderable": "sortable",  # Instead of `orderable`
                    "ascending": "ascend",  # Instead of `asc`
                    "descending": "descend",  # Instead of `desc`
                }
            }
        }

    def render_actions(self, value, record):
        # Customize the buttons and their behavior as needed
        accept_url = reverse("accept_day_off_trading", args=[record.id])
        reject_url = reverse("reject_day_off_trading", args=[record.id])

        accept_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#confirmModal" class="btn btn-success">Accept</a>',
            accept_url,
        )
        reject_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#rejectModal" class="btn btn-danger">Reject</a>',
            reject_url,
        )

        return format_html("{} {}", accept_button, reject_button)

    def render_created_At(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.created_At
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestee_swap_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestee_swap_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestee_trade_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestee_trade_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp


class DayOffTradingTableSupervisor(tables.Table):
    # Your existing columns go here
    requestor = tables.Column(
        verbose_name="Requestor",
        attrs={"width": "20%", "text-align": "center"},
    )
    requestor_swap_roster = tables.Column(
        verbose_name="Requestor\nSwap\nDate",
        accessor=Accessor("requestor_swap_roster"),
        orderable=True,
        attrs={"width": "20%", "text-align": "center"},
    )
    requestor_trade_roster = tables.Column(
        verbose_name="Requestor Trade Date",
        accessor=Accessor("requestor_trade_roster"),
        orderable=True,
    )
    requestee_swap_roster = tables.Column(
        verbose_name="Requestee Swap Date",
        accessor=Accessor("requestee_swap_roster"),
        orderable=True,
    )
    requestee_trade_roster = tables.Column(
        verbose_name="Requestee Trade Date",
        accessor=Accessor("requestee_trade_roster"),
        orderable=True,
    )
    created_At = tables.Column(verbose_name="Requested At", orderable=True)
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)

    # Define a custom column for "Accept" and "Reject" buttons
    class Meta:
        model = DayOffTrading
        ordering = "-created_At"
        sequence = (
            "requestor",
            "requestor_swap_roster",
            "requestor_trade_roster",
            "requestee",
            "requestee_swap_roster",
            "requestee_trade_roster",
        )
        exclude = (
            "id",
            "supervisor",
            "supervisor_approval_status",
            "supervisor_approval_status_datetime",
            "updated_At",
            "requestee_approval_status",
            "requestee_approval_status_datetime",
            "trading_status",
        )
        row_attrs = {"data-id": lambda record: record.id}
        attrs = {
            "th": {
                "_ordering": {
                    "orderable": "sortable",
                    "ascending": "ascend",
                    "descending": "descend",
                },
                "text-align": "center",
            },
            "td": {"text-align": "center"},
        }

    def render_actions(self, value, record):
        # Customize the buttons and their behavior as needed
        accept_url = reverse("accept_day_off_trading", args=[record.id])
        reject_url = reverse("reject_day_off_trading", args=[record.id])

        accept_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#confirmModal" class="btn btn-success">Accept</a>',
            accept_url,
        )
        reject_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#rejectModal" class="btn btn-danger">Reject</a>',
            reject_url,
        )

        return format_html("{} {}", accept_button, reject_button)

    def render_created_At(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.created_At
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestee_swap_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestee_swap_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestor_swap_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestor_swap_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestee_trade_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestee_trade_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestor_trade_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestor_trade_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp


class ShiftTimeTradingTableEmployee(tables.Table):
    # Your existing columns go here
    requestor = tables.Column(verbose_name="Requestor", attrs={"width": "20%"})
    requestor_swap_roster = tables.Column(
        verbose_name="Swap Date",
        accessor=Accessor("requestor_swap_roster"),
        orderable=True,
    )
    created_At = tables.Column(verbose_name="Requested At", orderable=True)
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)

    # Define a custom column for "Accept" and "Reject" buttons
    class Meta:
        model = ShiftTimeTrading
        ordering = "-created_At"
        sequence = (
            "requestor",
            "requestor_swap_roster",
            "requestor_start_time",
            "requestor_end_time",
            "requestee_start_time",
            "requestee_end_time"
            # "requestee_trade_roster",
        )
        exclude = (
            "id",
            "requestee",
            "requestee_swap_roster",
            "requestee_approval_status",
            "requestee_approval_status_datetime",
            "supervisor",
            "supervisor_approval_status",
            "supervisor_approval_status_datetime",
            "updated_At",
        )
        row_attrs = {"data-id": lambda record: record.id}
        attrs = {
            "th": {
                "_ordering": {
                    "orderable": "sortable",  # Instead of `orderable`
                    "ascending": "ascend",  # Instead of `asc`
                    "descending": "descend",  # Instead of `desc`
                }
            }
        }

    def render_actions(self, value, record):
        # Customize the buttons and their behavior as needed
        accept_url = reverse("accept_shift_time_trading", args=[record.id])
        reject_url = reverse("reject_shift_time_trading", args=[record.id])

        accept_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#confirmModal" class="btn btn-success">Accept</a>',
            accept_url,
        )
        reject_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#rejectModal" class="btn btn-danger">Reject</a>',
            reject_url,
        )

        return format_html("{} {}", accept_button, reject_button)

    def render_created_At(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.created_At
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestor_swap_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestee_swap_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp


class ShiftTimeTradingTableSupervisor(tables.Table):
    # Your existing columns go here
    requestor = tables.Column(verbose_name="Requestor", attrs={"width": "20%"})
    requestor_swap_roster = tables.Column(
        verbose_name="Swap Date",
        accessor=Accessor("requestor_swap_roster"),
        orderable=True,
    )
    created_At = tables.Column(verbose_name="Requested At", orderable=True)
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)

    # Define a custom column for "Accept" and "Reject" buttons
    class Meta:
        model = ShiftTimeTrading
        ordering = "-created_At"
        sequence = (
            "requestor",
            "requestor_swap_roster",
            "requestor_start_time",
            "requestor_end_time",
            "requestee",
            "requestee_start_time",
            "requestee_end_time",
        )
        exclude = (
            "id",
            "requestee_swap_roster",
            "requestee_approval_status",
            "requestee_approval_status_datetime",
            "supervisor",
            "supervisor_approval_status",
            "supervisor_approval_status_datetime",
            "updated_At",
        )
        row_attrs = {"data-id": lambda record: record.id}
        attrs = {
            "th": {
                "_ordering": {
                    "orderable": "sortable",  # Instead of `orderable`
                    "ascending": "ascend",  # Instead of `asc`
                    "descending": "descend",  # Instead of `desc`
                }
            }
        }

    def render_actions(self, value, record):
        # Customize the buttons and their behavior as needed
        accept_url = reverse("accept_shift_time_trading", args=[record.id])
        reject_url = reverse("reject_shift_time_trading", args=[record.id])

        accept_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#confirmModal" class="btn btn-success">Accept</a>',
            accept_url,
        )
        reject_button = format_html(
            '<a href="{}" data-toggle="modal" data-target="#rejectModal" class="btn btn-danger">Reject</a>',
            reject_url,
        )

        return format_html("{} {}", accept_button, reject_button)

    def render_created_At(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.created_At
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp

    def render_requestor_swap_roster(self, value, record):
        # Format the timestamp value to the desired format
        timestamp = record.requestee_swap_roster.start_date
        formatted_timestamp = timestamp.strftime("%Y-%m-%d")
        return formatted_timestamp
