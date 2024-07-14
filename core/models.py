from django.db import models
from django.contrib.auth.models import User
from django.apps import apps
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.ManyToManyField(Tag, related_name='problems')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Contest(models.Model):
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    problems = models.ManyToManyField(Problem, related_name='contests', blank=True)

    def __str__(self):
        return self.name

class User_Details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='details')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def user_created_at(self):
        return self.user.date_joined

    @property
    def user_last_login(self):
        return self.user.last_login

    @property
    def problems_solved(self):
        Submission = apps.get_model('coding', 'Submission')
        return Submission.objects.filter(user=self.user, status='Accepted').values('problem').distinct().count()
    
    # Remove the setter method to ensure read-only behavior
    @problems_solved.setter
    def problems_solved(self, value):
        pass

    class Meta:
        managed = True