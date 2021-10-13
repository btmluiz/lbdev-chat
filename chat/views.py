from django.shortcuts import render

# Create your views here.
from api.models import User
from lbdev_chat.settings import SITE_NAME, COMPANY_NAME, COMPANY_URL


def test_email(request):
    user = User.objects.all().get(username='luiz.braga')
    return render(request, 'email/password_recovery.html', {
        'code': "015867",
        'user': user,
        'site_name': SITE_NAME,
        'company_name': COMPANY_NAME,
        'company_url': COMPANY_URL,
    })
