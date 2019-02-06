from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserCreationForm, UserLogInForm

def home(request):
	template_name = "birthdate/home.html"

	status = None
	if request.GET.get('status') is not None:
		status = request.GET.get('status')

	context = { 
		'status': status
	}
	return render(request, template_name, context)

def about(request):
	template_name = "birthdate/about.html"

	context = { }

	return render(request, template_name, context)

def features(request):
	template_name = "birthdate/features.html"

	context = { }

	return render(request, template_name, context)

def pricing(request):
	template_name = "birthdate/pricing.html"

	context = { }

	return render(request, template_name, context)

def log_in(request):
    template_name = 'birthdate/log-in.html'
    form = UserLogInForm(request.POST or None)
    next = request.POST.get('next', request.GET.get('next', ''))

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if next:
                    return HttpResponseRedirect(next)
                print('logged in')
                return redirect('birthdate_dashboard')
            else: 
                #messages.error(request, "The username or password is incorrect.")
                print('username or password is incorrect')
        else: 
            #messages.error(request, "Something is going wrong...")
            print('form is invalid')

    context = {
        "section_header": "Account Access",
        "form": form,
    }

    return render(request, template_name, context)

def sign_up(request):
	template_name = "birthdate/sign-up.html"
	pricing_plan = request.GET.get('PP')

	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('birthdate_dashboard')
		else:
			print('form wasnt valid')
	else:
		form = UserCreationForm()

	context = { 
		'form': form,

	}
	return render(request, template_name, context)

def log_out(request):
	logout(request)
	return redirect('birthdate_home')

@login_required
def dashboard(request):
	template_name = "birthdate/dashboard/dashboard.html"
	context = { }
	return render(request, template_name, context)

@login_required
def template(request, public_key):
	template_name = "birthdate/dashboard/template.html"
	context = { }
	return render(request, template_name, context)