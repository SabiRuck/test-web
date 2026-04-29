from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Test 
from .forms import TestForm

@login_required
def dashboard(request):
    user_profil = request.user.profil 
    
    if user_profil.is_teacher:
        testy = Test.objects.all()
        # Musíme pridať {'testy': testy}, aby ich HTML videlo
        return render(request, 'quiz/ucitel_dashboard.html', {'testy': testy})
    else:
        testy = Test.objects.filter(is_published=True)
        return render(request, 'quiz/student_dashboard.html', {'testy': testy})
    
@login_required
def vytvor_test(request):
    if not request.user.profil.is_teacher:
        return redirect('index')

    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TestForm()
    
    return render(request, 'quiz/ucitel_dashboard.html', {
        'form': form, 
        'vytvaram_test': True,
        'testy': Test.objects.all()
    })

def index(request):
    return render(request, 'quiz/index.html')