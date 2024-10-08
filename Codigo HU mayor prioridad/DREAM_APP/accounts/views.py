from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import HttpResponse

def login_view(request):  
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('app')  
        else:
            return render(request, 'login_fail.html') 
    return render(request, 'login.html')