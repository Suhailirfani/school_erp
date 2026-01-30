from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def management_required(view_func):
    """Decorator to ensure only Management can access views"""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.user_type != 5:
            messages.error(request, 'Access denied. Management privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@management_required
def management_dashboard(request):
    """Management Dashboard"""
    context = {
        'page_title': 'Management Dashboard'
    }
    return render(request, 'Management/home.html', context)
