def run():
    workRule = WorkRule.objects.get(id=1)
    requestorRoster = Roster.objects.get(id=4179)
    requestee = Employee.objects.get(id=214096)
    requesteeRoster = Roster.objects.filter(
        Q(employee=requestee),
        Q(start_date=requestorRoster.start_date),
        Q(end_date=requestorRoster.end_date),
    ).first()
    requestorRegularShiftDurationResult, requestorRegularShiftDurationError = (
        checkRegularShiftDuration(
            roster=requestorRoster,
            workRule=workRule,
        )
    )