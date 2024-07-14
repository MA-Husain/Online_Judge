from django.urls import path
from django.contrib.auth import views as auth_view
from django.contrib.auth.decorators import login_required
from . import views
from . forms import Login_Form, MyPasswordRestForm, MyPasswordChangeForm, MyPasswordSetForm
from core import views as core_views


urlpatterns = [
    path("" , views.home, name="home"),
    path("about/" , views.about, name="about"),
    path("sections/<slug:val>", views.Sections_View.as_view(), name = "sections"),
    # path("problem_statement/<int:pk>", views.Problem_Statement.as_view(), name = "problem_statement"),
    path('sign-up/', views.Sign_Up_View.as_view(), name='sign-up'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    # path('confirm-otp/', views.Confirm_OTP_View.as_view(), name='confirm_otp'),
    path('profile/', views.profile_view, name='profile'),
    path('accounts/login/', auth_view.LoginView.as_view(template_name='app/login.html', authentication_form=Login_Form), name='login'),
    path('passwordchange/', login_required(auth_view.PasswordChangeView.as_view(template_name='app/password_change.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone')), name='passwordchange'),
    path('passwordchangedone/', login_required(auth_view.PasswordChangeDoneView.as_view(template_name='app/password_change_done.html')), name='passwordchangedone'),
    path('password-reset/', auth_view.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=MyPasswordRestForm), name='password_reset'),
    path('password-reset/done', auth_view.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html', form_class=MyPasswordSetForm), name='password_reset_confirm'),
    path('password-reset-complete/', auth_view.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name='password_reset_complete'),
    path('logout/', views.logout, name='logout'),
    path('create-problem/', views.create_problem_and_add_test_cases, name='create_problem_and_add_test_cases'),
    path('add-test-cases/<int:problem_id>/', views.add_test_cases, name='add_test_cases'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('problem/search/', views.problem_search, name='problem_search'),
]