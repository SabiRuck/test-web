from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import formset_factory
from .models import Test, Trieda, Profil, Question, Answer, TestQuestion
from .forms import TestForm, TriedaForm, ProfilTriedaForm, QuestionForm, AnswerForm


def is_teacher_or_staff(user):
    try:
        return user.profil.is_teacher or user.is_staff
    except Profil.DoesNotExist:
        return user.is_staff


# ── INDEX ──────────────────────────────────────────────────────

def index(request):
    return render(request, 'quiz/index.html')


# ── DASHBOARD ─────────────────────────────────────────────────

@login_required
def dashboard(request):
    # Auto-create Profil if missing (e.g. admin created via command line)
    profil, _ = Profil.objects.get_or_create(user=request.user)

    if is_teacher_or_staff(request.user):
        testy = Test.objects.prefetch_related('assigned_classes').all()
        return render(request, 'quiz/ucitel_dashboard.html', {'testy': testy})
    else:
        testy = Test.objects.filter(is_published=True)
        return render(request, 'quiz/student_dashboard.html', {'testy': testy})


# ── TESTY (UČITEĽ) ────────────────────────────────────────────

@login_required
def vytvor_test(request):
    if not is_teacher_or_staff(request.user):
        return redirect('index')

    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save()
            return redirect('detail_testu', test_id=test.id)
    else:
        form = TestForm()

    return render(request, 'quiz/vytvor_test.html', {'form': form})


@login_required
def detail_testu(request, test_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    test = get_object_or_404(Test, id=test_id)
    test_otazky = TestQuestion.objects.filter(test=test).select_related('question').order_by('order')
    return render(request, 'quiz/detail_testu.html', {
        'test': test,
        'test_otazky': test_otazky,
    })


@login_required
def vytvor_otazku(request, test_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    test = get_object_or_404(Test, id=test_id)
    AnswerFormSet = formset_factory(AnswerForm, extra=4)

    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        a_formset = AnswerFormSet(request.POST, prefix='odpovede')
        if q_form.is_valid() and a_formset.is_valid():
            otazka = q_form.save()
            for a_form in a_formset:
                if a_form.cleaned_data.get('text'):
                    Answer.objects.create(
                        question=otazka,
                        text=a_form.cleaned_data['text'],
                        is_correct=a_form.cleaned_data.get('is_correct', False),
                    )
            poradie = TestQuestion.objects.filter(test=test).count() + 1
            TestQuestion.objects.create(test=test, question=otazka, order=poradie)
            return redirect('detail_testu', test_id=test.id)
    else:
        q_form = QuestionForm()
        a_formset = AnswerFormSet(prefix='odpovede')

    return render(request, 'quiz/vytvor_otazku.html', {
        'test': test,
        'q_form': q_form,
        'a_formset': a_formset,
    })


@login_required
def zmaz_otazku_z_testu(request, test_id, tq_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    tq = get_object_or_404(TestQuestion, id=tq_id, test_id=test_id)
    if request.method == 'POST':
        tq.delete()
    return redirect('detail_testu', test_id=test_id)


@login_required
def banka_otazok(request, test_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    test = get_object_or_404(Test, id=test_id)
    uz_pridane_ids = set(
        TestQuestion.objects.filter(test=test).values_list('question_id', flat=True)
    )
    vsetky_otazky = Question.objects.prefetch_related('answers').all()
    hladaj = request.GET.get('q', '')
    if hladaj:
        vsetky_otazky = vsetky_otazky.filter(text__icontains=hladaj)

    return render(request, 'quiz/banka_otazok.html', {
        'test': test,
        'vsetky_otazky': vsetky_otazky,
        'uz_pridane_ids': uz_pridane_ids,
        'hladaj': hladaj,
    })


@login_required
def pridaj_otazku_z_banky(request, test_id, question_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    test = get_object_or_404(Test, id=test_id)
    otazka = get_object_or_404(Question, id=question_id)
    if not TestQuestion.objects.filter(test=test, question=otazka).exists():
        poradie = TestQuestion.objects.filter(test=test).count() + 1
        TestQuestion.objects.create(test=test, question=otazka, order=poradie)
    hladaj = request.GET.get('q', '')
    url = f"/test/{test_id}/banka/"
    if hladaj:
        url += f"?q={hladaj}"
    return redirect(url)


# ── SPRÁVA TRIED (len admin) ──────────────────────────────────

@login_required
def sprava_tried(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST' and 'vytvor_triedu' in request.POST:
        form = TriedaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sprava_tried')
    else:
        form = TriedaForm()

    triedy = Trieda.objects.all().prefetch_related('studenti__user')
    zaci_bez_triedy = Profil.objects.filter(is_teacher=False, trieda=None)

    return render(request, 'quiz/sprava_tried.html', {
        'triedy': triedy,
        'form': form,
        'zaci_bez_triedy': zaci_bez_triedy,
    })


@login_required
def zmaz_triedu(request, trieda_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    trieda = get_object_or_404(Trieda, id=trieda_id)
    if request.method == 'POST':
        trieda.delete()
    return redirect('sprava_tried')


@login_required
def zarad_ziaka(request, profil_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    profil = get_object_or_404(Profil, id=profil_id)
    if request.method == 'POST':
        form = ProfilTriedaForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
    return redirect('sprava_tried')