from accounts.models import *
from django.db.models import Func, F, Value
from django.db.models.functions import Substr


class EmailDomain(Func):
    function = "SUBSTRING_INDEX"
    template = "%(function)s(%(expressions)s,'@',-1)"


def run():
    distinct_domains = (
        CustomUser.objects.annotate(domain=EmailDomain("email"))
        .values("domain")
        .distinct()
    )
    for domain in distinct_domains:
        print(domain["domain"])
