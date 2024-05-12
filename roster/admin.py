from django.contrib import admin
from .models import Roster, ShiftLegend, WorkRule, RosterCount, RosterSeatCount

# Register your models here.
admin.site.register(Roster)
admin.site.register(WorkRule)
admin.site.register(RosterCount)
admin.site.register(RosterSeatCount)
admin.site.register(ShiftLegend)
