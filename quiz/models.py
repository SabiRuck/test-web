from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Trieda(models.Model):
    nazov = models.CharField(max_length=10, unique=True)
    class Meta:
        verbose_name_plural = "Triedy"
    def __str__(self):
        return self.nazov
    

# Create your models here.
class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    vek = models.PositiveIntegerField(null=True, blank=True)
    is_teacher = models.BooleanField(default=False)
    trieda = models.ForeignKey(Trieda, on_delete=models.SET_NULL, null=True, blank=True, related_name='studenti')

    def __str__(self):
        # Ak má vyplnené meno alebo priezvisko, vráti ich spojené. Inak vráti prihlasovacie meno.
        if self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return self.user.username
    

class Question(models.Model):
    TYPES = [
        ('SC', 'Single Choice'),
        ('MC', 'Multiple Choice'),
        ('TXT', 'Short Answer'),
    ]
    text = models.TextField()
    type = models.CharField(max_length=3, choices=TYPES)
    points = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='otazky')

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
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='testy')

    # --- NOVÉ POLE PRE PRIRADENIE TRIED ---
    # Učiteľ môže vybrať viac tried pre jeden test
    assigned_classes = models.ManyToManyField(Trieda, related_name='tests', blank=True)
    questions = models.ManyToManyField(Question, related_name='tests', through='TestQuestion')

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
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    score = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Tu sa namiesto škaredého username zobrazí pekné meno študenta pri výsledku testu
        if self.user.first_name or self.user.last_name:
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            return f"{full_name} - {self.test.title}"
        return f"{self.user.username} - {self.test.title}"

    
class StudentResponse(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)