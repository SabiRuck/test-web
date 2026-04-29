from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # request.user je prihlásený Django User
    # .profil je tvoj model, kde máš is_teacher
    
    user_profil = request.user.profil 
    
    if user_profil.is_teacher:
        return render(request, 'quiz/ucitel_dashboard.html')
    else:
        return render(request, 'quiz/student_dashboard.html')

def index(request):
    return render(request, 'quiz/index.html')