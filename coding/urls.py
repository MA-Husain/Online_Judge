
from django.urls import path
from . import views
from .views import SubmitCodeView, ProblemDetailView

urlpatterns = [
    # Ensure 'submit_code' URL is correctly defined, possibly like this:
    path('problem/<int:pk>/submit/', SubmitCodeView.as_view(), name='submit_code'),
    path('problem/<int:pk>/', ProblemDetailView.as_view(), name='problem_detail'),
    path('problem/<int:problem_id>/all-submissions/', views.all_submissions, name='all_submissions'),
    path('problem/<int:problem_id>/my_submissions/', views.my_submissions, name='my_submissions'),
    path('submission/code/<uuid:submission_id>/', views.get_submission_code, name='get_submission_code'),
    path('my_all_submissions/', views.my_all_submissions, name='my_all_submissions'),
    path('my_all_submissions/<uuid:problem_id>/', views.my_all_submissions, name='my_submissions_by_problem'),
    # Other paths
]