from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # NOTE: key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold font from the context"}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # NOTE: the first parameter is the template we wish to use
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = {'boldmessage': "ABOUT RANGO"}
    return render(request, 'rango/about.html', context_dict)

