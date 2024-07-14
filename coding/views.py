from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from core.models import Problem
from .models import Submission, TestCase, SubmissionTestCase
from django.utils.decorators import method_decorator
from .forms import CodeSubmissionForm
from .utils import handle_run, handle_submit
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@method_decorator(login_required, name='dispatch')
class ProblemDetailView(View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        form = CodeSubmissionForm(initial={
            'language': request.session.get('initial_language', ''),
            'code': request.session.get('initial_code', ''),
            'input_data': request.session.get('initial_input_data', ''),
        })

        context = {
            'problem': problem,
            'form': form,
        }

        # Clear the session data after retrieving it
        request.session.pop('initial_language', None)
        request.session.pop('initial_code', None)
        request.session.pop('initial_input_data', None)

        return render(request, 'coding/problem_detail.html', context)
    
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        form = CodeSubmissionForm(request.POST)
        
        if form.is_valid():
            language = form.cleaned_data.get('language')
            code = form.cleaned_data.get('code')
            input_data = form.cleaned_data.get('input_data')

            request.session['initial_language'] = language
            request.session['initial_code'] = code
            request.session['initial_input_data'] = input_data

            if 'run' in request.POST:
                return handle_run(request, form, problem)
            elif 'submit' in request.POST:
                return handle_submit(request, form, problem, pk)
        else:
            request.session['initial_language'] = form.cleaned_data.get('language')
            request.session['initial_code'] = form.cleaned_data.get('code')
            request.session['initial_input_data'] = form.cleaned_data.get('input_data')

        context = {
            'problem': problem,
            'form': form,
            'error': 'Invalid form submission',
        }
        return render(request, 'coding/problem_detail.html', context)

@method_decorator(login_required, name='dispatch')
class SubmitCodeView(View):
    def get(self, request, pk):
        context = {'pk': pk}

        return render(request, 'coding/submit_code.html', context)
    
@login_required(login_url='login')   
def all_submissions(request, problem_id):
    submissions = Submission.objects.filter(problem_id=problem_id).order_by('-created_at').values(
        'id', 'user__username', 'status', 'language', 'created_at', 'code'
    )
    return JsonResponse({'submissions': list(submissions)})

@login_required(login_url='login')
def my_submissions(request, problem_id):
    submissions = Submission.objects.filter(problem_id=problem_id, user=request.user).order_by('-created_at').values(
        'id', 'user__username', 'status', 'language', 'created_at', 'code'
    )
    return JsonResponse({'submissions': list(submissions)})

def get_submission_code(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return JsonResponse({'code': submission.code})

@login_required(login_url='login') 
def my_all_submissions(request, problem_id=None):
    if problem_id:
        problem = get_object_or_404(Problem, id=problem_id)
        submissions = Submission.objects.filter(user=request.user, problem=problem).order_by('-created_at')
    else:
        submissions = Submission.objects.filter(user=request.user).order_by('-created_at')

    paginator = Paginator(submissions, 15)  # Show 15 submissions per page
    page = request.GET.get('page', 1)

    try:
        paginated_submissions = paginator.page(page)
    except PageNotAnInteger:
        paginated_submissions = paginator.page(1)
    except EmptyPage:
        paginated_submissions = paginator.page(paginator.num_pages)

    return render(request, 'coding/my_all_submissions.html', {'submissions': paginated_submissions})