from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.views import View
from urllib import request
from . models import Problem, Tag, User_Details, Contest
from . forms import Sign_Up_form, UserProfileForm, CreateProblemForm, CreateTestCaseForm, BaseTestCaseFormSet
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User, auth
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms import formset_factory
from django.core.paginator import Paginator
from django.db.models import Count, Max, Q


# Create your views here.
def home(request):
    return render(request, "app/home.html")

def about(request):
    return render(request, "app/about.html")

class Sections_View(View):
    def get(self, request, val):
        # Map the URL value to the tag's name
        tag_map = {
            'arrays': 'Arrays',
            'BS': 'Binary Search',
            'DP': 'Dynamic Programming',
            'graphs': 'Graphs'
        }
        
        # Get the corresponding tag name
        tag_name = tag_map.get(val)
        
        if not tag_name:
            # If the tag name does not exist, return a 404 error
            return render(request, '404.html', status=404)
        
        # Get the Tag object based on the section name (val)
        tag = get_object_or_404(Tag, name=tag_name)
        
        # Retrieve all problems associated with the tag
        problems = tag.problems.all()

        context = {
            'tag': tag, 
            'problems': problems,
        }
        
        return render(request, 'app/sections.html', context)




from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

class Sign_Up_View(View):
    def get(self, request):
        form = Sign_Up_form()
        context = {'form': form}
        return render(request, 'app/signup.html', context)
    
    def post(self, request):
        form = Sign_Up_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until it is confirmed
            user.save()
            
            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('app/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_mail(mail_subject, message, 'picodetoinspire@gmail.com', [to_email])
            
            messages.success(request, "Please check your email and follow the link to complete the registration. Do check the spam folder also.")
            return render(request, 'app/signup.html', {'form': form})  # Render the signup form again with success message
        else:
            return render(request, 'app/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('login')  # Redirect to login after successful activation
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('home')  # Redirect to home if activation fails
    
@login_required(login_url='login')
def profile_view(request):
    user_details, created = User_Details.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_details, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_details, user=request.user)
    
    # Check if the user wants to edit their profile
    if 'edit' in request.GET or not user_details.name or not user_details.location:
        return render(request, 'app/profile_edit.html', {'form': form})

    # Fetch additional user info
    profile_info = {
        'username': request.user.username,
        'email': user_details.email,
        'name': user_details.name,
        'location': user_details.location,
        'created_at': request.user.date_joined,
        'last_login': request.user.last_login,
        # Assuming you have a method or attribute to fetch problems solved
        'problems_solved': user_details.problems_solved,
        
    }

    return render(request, 'app/profile.html', {'profile_info': profile_info})

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def create_problem_and_add_test_cases(request):
    if not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':
        problem_form = CreateProblemForm(request.POST)
        if problem_form.is_valid():
            problem = problem_form.save()
            problem_form.instance.tags.set(problem_form.cleaned_data['tags'])  # Set the tags manually
            return redirect('add_test_cases', problem_id=problem.id)
    else:
        problem_form = CreateProblemForm()

    context = {
        'problem_form': problem_form,
    }
    return render(request, 'app/create_problem.html', context)

@login_required(login_url='login')
def add_test_cases(request, problem_id):
    if not request.user.is_staff:
        return redirect('home')
    problem = get_object_or_404(Problem, pk=problem_id)
    TestCaseFormset = formset_factory(CreateTestCaseForm, formset=BaseTestCaseFormSet, extra=1)

    if request.method == 'POST':
        formset = TestCaseFormset(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    test_case = form.save(commit=False)
                    test_case.problem = problem
                    test_case.save()
            return redirect('problem_detail', pk=problem.pk)
    else:
        formset = TestCaseFormset()

    context = {
        'problem': problem,
        'formset': formset,
    }
    return render(request, 'app/add_test_cases.html', context)

@login_required(login_url='login')
def leaderboard(request):
    user_details = User_Details.objects.all()

    # Create a list of user details with additional properties for sorting
    leaderboard_data = [
        {
            'user': user_detail.user,
            'problems_solved': user_detail.problems_solved,
            'last_solved_date': user_detail.user.submissions.filter(status='Accepted').aggregate(last_solved_date=Max('created_at'))['last_solved_date']
        }
        for user_detail in user_details
    ]

    # Sort the leaderboard data by problems solved and last solved date
    leaderboard_data.sort(key=lambda x: (-x['problems_solved'], x['last_solved_date'].timestamp() if x['last_solved_date'] else 0))

    paginator = Paginator(leaderboard_data, 15)  # Show 15 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'leaderboard_data': page_obj,
    }
    return render(request, 'app/leaderboard.html', context)

@login_required
def problem_search(request):
    query = request.GET.get('q')
    if query:
        problems = Problem.objects.filter(
            Q(title__icontains=query) |  # Search by title
            Q(description__icontains=query)  # Search by description
        ).distinct()
    else:
        problems = Problem.objects.all()

    context = {
        'problems': problems,
        'query': query
    }
    return render(request, 'app/problem_search.html', context)