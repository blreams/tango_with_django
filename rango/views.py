from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there world!<p><a href=/rango/about/>About Page</a></p>")

def about(request):
    return HttpResponse("Rango says here is the about page.<p><a href=/rango/>Main Page</a></p>")

