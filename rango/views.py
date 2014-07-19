from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from rango.models import Category, Page, UserProfile
from datetime import datetime
from rango.bing_search import run_query
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User

def encode_url(str):
	return str.replace(' ', '_')

def decode_url(str):
	return str.replace('_', ' ')


def index(request):
	# Request the context of the request.
    # The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	# Query Database for the list of all lists
	# Order categories by no. of likes in descending order.
	# Retreive the top 5 only - or all if less than 5
	# Place the list in our our context_dict
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	# Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
	context_dict = {'boldmessage': "I'm Bold font from the context",
		'categories': category_list}
	context_dict['pages'] = page_list

	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list

	for category in category_list:
		category.url = encode_url(category.name)

	# Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.

	if request.session.get('last_visit'):
		last_visit_time = request.session.get('last_visit')
		visits = request.session.get('visits',0)

		if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
			request.session['visits'] = visits + 1
			request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = 1

	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	context = RequestContext(request)

	context_dict = {'titlemessage': "I'm h3 message"}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list

	return render_to_response('rango/about.html',context_dict, context)

def category(request, category_name_url):
	# Request our context from request
	context = RequestContext(request)

	# change underscores in category name to spaces
	category_name = decode_url(category_name_url)

	# create context dictionary to pass to template
	context_dict = {'category_name': category_name}
	context_dict['category_name_url'] = encode_url(category_name_url)
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list

	try:
		category = Category.objects.get(name=category_name)

		pages = Page.objects.filter(category=category).order_by('-views')

		# Add pages and category to the context dicitionary
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		pass

	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			result_list = run_query(query)
			context_dict['result_list'] = result_list

	return render_to_response('rango/category.html', context_dict, context)



@login_required
def add_category(request):
	context = RequestContext(request)

	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)

			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()

	return render_to_response('rango/add_category.html', {'form': form}, context)


@login_required
def add_page(request, category_name_url):
	context = RequestContext(request)

	category_name = decode_url(category_name_url)

	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			page = form.save(commit=False)

			try:
				cat = Category.objects.get(name=category_name)
				page.category = cat
			except Category.DoesNotExist:
				return render_to_response('/rango/add_category.html')

			page.views = 0;

			page.save()

			return category(request, category_name_url)
		else:
			print form.errors
	else:
		form = PageForm()

	return render_to_response('rango/add_page.html', {'category_name_url':category_name_url,
			'category_name':category_name, 'form':form}, context)


def register(request):
	context = RequestContext(request)

	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True

		else:
			print user_form.errors, profile_form.errors
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response(
		'rango/register.html',
		{'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
		context)



def user_login(request):
	context = RequestContext(request)

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse("Your Rango account is disabled.")
		else:
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")
	else:
		return render_to_response('rango/login.html', {}, context)


@login_required
def restricted(request):
	context = RequestContext(request)
	return render_to_response('rango/restricted.html', {}, context)







@login_required
def user_logout(request):
	logout(request)

	return index(request)


def search(request):
	context = RequestContext(request)
	result_list = []

	if request.method == 'POST':
		query = request.POST['query'].strip()

		if query:
			result_list = run_query(query)

	return render_to_response('rango/search.html', {'result_list' : result_list}, context)


def get_category_list():
	cat_list = Category.objects.all()

	for cat in cat_list:
		cat.url = encode_url(cat.name)

	return cat_list

@login_required
def profile(request):
	context = RequestContext(request)
	cat_list = get_category_list()
	context_dict = {'cat_list': cat_list}
	u = User.objects.get(username=request.user)

	try:
		up = UserProfile.objects.get(user=u)
	except:
		up = None

	context_dict['user'] = u
	context_dict['userprofile'] = up

	return render_to_response('rango/profile.html', context_dict, context)


def track_url(request):
	context = RequestContext(request)
	page_id = None
	url = '/rango/'
	print "\n>>>>>>>" + request.GET['page_id']
	if request.method == 'GET':
		#if 'page_id' in request.GET['page_id']:
		page_id = request.GET['page_id']
		try:
			page = Page.objects.get(id=page_id)
			page.views = page.views + 1
			page.save()
			url = page.url
		except:
			print "\n>>>>>>> Exception occured"
			pass

	return redirect(url)

@login_required
def like_category(request):
	context = RequestContext(request)
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']

	likes = 0
	if cat_id:
		category = Category.objects.get(id=int(cat_id))
		if category:
			likes = category.likes + 1
			category.likes = likes
			category.save()

	return HttpResponse(likes)


def suggest_category(request):
	context = RequestContext(request)
	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']

	cat_list = get_category_list(8, starts_with)

	#return HttpResponse(cat_list)
	return render_to_response('rango/category_list.html', {'cat_list' : cat_list}, context)



def get_category_list(max_results=0, starts_with=''):
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__istartswith=starts_with)
	else:
		cat_list = Category.objects.all()
	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]

	for cat in cat_list:
		cat.url = encode_url(cat.name)

	return cat_list



