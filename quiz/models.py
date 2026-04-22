from django.db import models


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    meno = models.CharField(max_length=100)
    priezvisko = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    vek = models.PositiveIntegerField(null=True, blank=True)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({'Učiteľ' if self.is_teacher else 'Študent'})"
    

class Question(models.Model):
    TYPES = [
        ('SC', 'Single Choice'),
        ('MC', 'Multiple Choice'),
        ('TXT', 'Short Answer'),
    ]
    text = models.TextField()
    type = models.CharField(max_length=3, choices=TYPES)
    points = models.IntegerField(default=1) 

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text} - {self.text}"

class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=100)
    time_limit = models.IntegerField(help_text="Limit v minútach")
    is_published = models.BooleanField(default=False)

    questions = models.ManyToManyField(Question, evangelical='tests', through='TestQuestion')

    def __str__(self):
        return self.title

class TestQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    points_in_test = models.IntegerField(default=1) 

    class Meta:
        ordering = ['order']

class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)

class StudentResponse(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)