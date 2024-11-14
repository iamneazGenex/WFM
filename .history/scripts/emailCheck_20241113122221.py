from accounts.models import *


def run():
    customUser = CustomUser.objects.value("email")
