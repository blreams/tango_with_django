from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
#UNUSED#from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.bing_search import run_query

# Helper function
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 1:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits

    context_dict['visits'] = visits
    response = render(request, 'rango/index.html', context_dict)
    return response

def about(request):
    visits = request.session.get('visits')
    if not visits:
        visits = 0
    context_dict = {'boldmessage': "ABOUT RANGO", 'visits': visits}
    return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the result list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category.slug
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)
    return render(request, 'rango/category_list.html', {'cat_list': cat_list})

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

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)

#UNUSED#def register(request):
#UNUSED#    # A boolean value for telling the template whether the registration was successful.
#UNUSED#    # Initially set to False, will change to True if registration is successful.
#UNUSED#    registered = False
#UNUSED#
#UNUSED#    # POST method, process form data
#UNUSED#    if request.method == 'POST':
#UNUSED#        # Grab info from raw form, note use of both UserForm and UserProfileForm
#UNUSED#        user_form = UserForm(data=request.POST)
#UNUSED#        profile_form = UserProfileForm(data=request.POST)
#UNUSED#
#UNUSED#        if user_form.is_valid() and profile_form.is_valid():
#UNUSED#            user = user_form.save()
#UNUSED#
#UNUSED#            # Now hash the password
#UNUSED#            user.set_password(user.password)
#UNUSED#            user.save()
#UNUSED#
#UNUSED#            # Sort out the UserProfile instance
#UNUSED#            # Since we need to set the user attribute ourselves, we set commit=False.
#UNUSED#            # This delays saving the model until we are ready, to avoid integrity problems.
#UNUSED#            profile = profile_form.save(commit=False)
#UNUSED#            profile.user = user
#UNUSED#
#UNUSED#            # Did the user provide a profile picture?
#UNUSED#            if 'picture' in request.FILES:
#UNUSED#                profile.picture = request.FILES['picture']
#UNUSED#
#UNUSED#            # Now save the UserProfile model instance
#UNUSED#            profile.save()
#UNUSED#
#UNUSED#            # Update our variable to tell the template registration succeeded
#UNUSED#            registered = True
#UNUSED#
#UNUSED#        # Invalid form or forms, mistakes or something else?
#UNUSED#        # Print problems to the terminal and show to user
#UNUSED#        else:
#UNUSED#            print user_form.errors, profile_form.errors
#UNUSED#
#UNUSED#    # Not a POST method, so render form using two ModelForm instances.
#UNUSED#    # Forms will be blank, ready for user input.
#UNUSED#    else:
#UNUSED#        user_form = UserForm()
#UNUSED#        profile_form = UserProfileForm()
#UNUSED#
#UNUSED#    # Render template depending on context.
#UNUSED#    return render(request,
#UNUSED#            'rango/register.html',
#UNUSED#            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
#UNUSED#            )

#UNUSED#def user_login(request):
#UNUSED#    # POST method, try to pull relevent info
#UNUSED#    if request.method == 'POST':
#UNUSED#        # Gather username and password provided by the user from login form.
#UNUSED#        username = request.POST['username']
#UNUSED#        password = request.POST['password']
#UNUSED#
#UNUSED#        # User django machinery to see if username/password is valid.
#UNUSED#        user = authenticate(username=username, password=password)
#UNUSED#
#UNUSED#        # user is None if authentication failed
#UNUSED#        if user:
#UNUSED#            # Is the account active (ie. not disabled)?
#UNUSED#            if user.is_active:
#UNUSED#                # Valid, active user, we can login the user
#UNUSED#                login(request, user)
#UNUSED#                return HttpResponseRedirect('/rango/')
#UNUSED#            else:
#UNUSED#                # This is an inactive user
#UNUSED#                return HttpResponse("Your rango account is disabled.")
#UNUSED#        else:
#UNUSED#            # Failed login credentials
#UNUSED#            print "Invalid login credentials: {0}, {1}".format(username, password)
#UNUSED#            return HttpResponse("Invalid login credentials supplied.")
#UNUSED#
#UNUSED#    # The request is not a POST, so display the login form (ie. GET)
#UNUSED#    else:
#UNUSED#        return render(request, 'rango/login.html', {})

#UNUSED#@login_required
#UNUSED#def user_logout(request):
#UNUSED#    logout(request)
#UNUSED#    return HttpResponseRedirect('/rango/')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

