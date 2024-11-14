from accounts.models import *
from django.db.models import Func, F, Value
from django.db.models.functions import Substr


class EmailDomain(Func):
    function = "SUBSTRING_INDEX"
    template = "%(function)s(%(expressions)s,'@',-1)"


def run():
    customUser = CustomUser.objects.value("email")
