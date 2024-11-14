from accounts.models import *

class EmailDomain(Func):
    
def run():
    customUser = CustomUser.objects.value("email")
