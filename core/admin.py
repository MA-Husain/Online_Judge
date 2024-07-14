from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Problem, Contest, Tag, User_Details
from coding.models import TestCase, Submission, SubmissionTestCase
from django.utils import timezone

# Unregister the default User admin
admin.site.unregister(User)

# Register the User with a custom UserAdmin
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login')
    search_fields = ('username', 'email')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('-date_joined')

    def save_model(self, request, obj, form, change):
        """Override save_model to set created_at and updated_at"""
        if not obj.pk:
            obj.date_joined = timezone.now()
        obj.save()

# Inline admin for TestCase
class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 0  # Number of extra forms to display

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('difficulty', 'tags')
    filter_horizontal = ('tags',)
    inlines = [TestCaseInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'difficulty', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('input', 'expected_output', 'problem')
    search_fields = ('input', 'expected_output', 'problem__title')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'problem__title')

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'created_at', 'updated_at')
    list_filter = ('start_time', 'end_time')
    search_fields = ('name',)

@admin.register(User_Details)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'location', 'user_created_at', 'user_last_login', 'problems_solved')
    search_fields = ('user__username', 'name', 'location')
    readonly_fields = ('user_created_at', 'user_last_login', 'problems_solved')


admin.site.register(SubmissionTestCase)