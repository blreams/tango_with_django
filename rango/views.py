from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):
    context_dict = {}
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = {'boldmessage': "ABOUT RANGO"}
    return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):
    # Create a context dict which we can pass to the template rendering engine
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category.slug
    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # Probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    # A boolean value for telling the template whether the registration was successful.
    # Initially set to False, will change to True if registration is successful.
    registered = False

    # POST method, process form data
    if request.method == 'POST':
        # Grab info from raw form, note use of both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # Now hash the password
            user.set_password(user.password)
            user.save()

            # Sort out the UserProfile instance
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we are ready, to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now save the UserProfile model instance
            profile.save()

            # Update our variable to tell the template registration succeeded
            registered = True

        # Invalid form or forms, mistakes or something else?
        # Print problems to the terminal and show to user
        else:
            print user_form.errors, profile_form.errors

    # Not a POST method, so render form using two ModelForm instances.
    # Forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render template depending on context.
    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            )

def user_login(request):
    # POST method, try to pull relevent info
    if request.method == 'POST':
        # Gather username and password provided by the user from login form.
        username = request.POST['username']
        password = request.POST['password']

        # User django machinery to see if username/password is valid.
        user = authenticate(username=username, password=password)

        # user is None if authentication failed
        if user:
            # Is the account active (ie. not disabled)?
            if user.is_active:
                # Valid, active user, we can login the user
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # This is an inactive user
                return HttpResponse("Your rango account is disabled.")
        else:
            # Failed login credentials
            print "Invalid login credentials: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login credentials supplied.")

    # The request is not a POST, so display the login form (ie. GET)
    else:
        return render(request, 'rango/login.html', {})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

