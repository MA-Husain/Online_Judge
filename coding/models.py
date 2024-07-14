import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TestCase(models.Model):
    input = models.TextField()
    expected_output = models.TextField()
    problem = models.ForeignKey('core.Problem', on_delete=models.CASCADE, related_name='test_cases')

    def __str__(self):
        return f'Test Case for {self.problem.title}'

class Submission(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey('core.Problem', on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=50)
    status = models.CharField(max_length=100, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Submission by {self.user.username} for {self.problem.title}'

class SubmissionTestCase(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='submission_test_cases')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return f'Test Case {self.test_case.id} for Submission {self.submission.id}'