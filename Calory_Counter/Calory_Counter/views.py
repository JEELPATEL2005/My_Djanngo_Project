from django.shortcuts import render
from django.http import HttpResponse



def Home(request):
    return render(request, 'index.html')
    # return HttpResponse"<h1>This is Home Page</h1>")

def About(request):
    return HttpResponse("<h1>This is About Page</h1>")