from django.shortcuts import render

def domov_view(request):
    return render(request, 'index.html')