from django import forms
from .models import Test, Trieda, Profil, Question, Answer

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'subject', 'time_limit', 'assigned_classes', 'is_published']
        labels = {
            'title': 'Názov testu',
            'description': 'Popis',
            'subject': 'Predmet',
            'time_limit': 'Časový limit (minúty)',
            'assigned_classes': 'Triedy (môžeš vybrať viac)',
            'is_published': 'Zverejniť test',
        }
        widgets = {
            'assigned_classes': forms.CheckboxSelectMultiple(),
        }

class TriedaForm(forms.ModelForm):
    class Meta:
        model = Trieda
        fields = ['nazov']
        labels = {'nazov': 'Názov triedy (napr. 3A)'}

class ProfilTriedaForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['trieda']
        labels = {'trieda': 'Zaradiť do triedy'}

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'type', 'points']
        labels = {
            'text': 'Text otázky',
            'type': 'Typ otázky',
            'points': 'Počet bodov',
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        labels = {
            'text': 'Text odpovede',
            'is_correct': 'Správna odpoveď?',
        }