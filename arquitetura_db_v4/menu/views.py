from django.shortcuts import render
from core.utils import session_login_required

@session_login_required
def index(request):
    return render(request, 'menu/index.html')
