from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import formset_factory
from .forms import TestForm, TriedaForm, ProfilTriedaForm, QuestionForm, AnswerForm
from .models import Test, Trieda, Profil, Question, Answer, TestQuestion, Result, StudentResponse

def is_teacher_or_staff(user):
    try:
        return user.profil.is_teacher or user.is_staff
    except Profil.DoesNotExist:
        return user.is_staff


# ── INDEX ──────────────────────────────────────────────────────

def index(request):
    # Ak už užívateľ je prihlásený, pošli ho na dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    # Ak nie je prihlásený, ukáž mu index.html, kde v lište bude svietiť "Prihlásiť sa"
    return render(request, 'quiz/index.html')


# ── DASHBOARD ─────────────────────────────────────────────────
@login_required
def dashboard(request):
    profil, _ = Profil.objects.get_or_create(user=request.user)

    if is_teacher_or_staff(request.user):
        if request.user.is_staff:
            testy = Test.objects.prefetch_related('assigned_classes').all()
        else:
            testy = Test.objects.prefetch_related('assigned_classes').filter(created_by=request.user)

        publikovany_filter = request.GET.get('publikovany', '')
        trieda_filter = request.GET.get('trieda', '')
        predmet_filter = request.GET.get('predmet', '')

        if publikovany_filter == '1':
            testy = testy.filter(is_published=True)
        elif publikovany_filter == '0':
            testy = testy.filter(is_published=False)

        if trieda_filter:
            testy = testy.filter(assigned_classes__nazov=trieda_filter)

        if predmet_filter:
            testy = testy.filter(subject__icontains=predmet_filter)

        triedy = Trieda.objects.all()

        return render(request, 'quiz/ucitel_dashboard.html', {
            'testy': testy,
            'triedy': triedy,
            'publikovany_filter': publikovany_filter,
            'trieda_filter': trieda_filter,
            'predmet_filter': predmet_filter,
        })
    else:
        predmet_filter = request.GET.get('predmet', '')

        vsetky_testy = Test.objects.filter(is_published=True, assigned_classes=profil.trieda)

        if predmet_filter:
            vsetky_testy = vsetky_testy.filter(subject__icontains=predmet_filter)

        vypracovane_ids = Result.objects.filter(user=request.user).values_list('test_id', flat=True)
        nove_testy = vsetky_testy.exclude(id__in=vypracovane_ids)
        vysledky = Result.objects.filter(user=request.user).select_related('test').order_by('-completed_at')

        return render(request, 'quiz/student_dashboard.html', {
            'nove_testy': nove_testy,
            'vysledky': vysledky,
            'predmet_filter': predmet_filter,
        })
    
# ── TESTY (UČITEĽ) ────────────────────────────────────────────

@login_required
def vytvor_test(request):
    if not is_teacher_or_staff(request.user):
        return redirect('index')

    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.created_by = request.user
            test.save()
            form.save_m2m()
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
    
    for tq in test_otazky:
        otazka = tq.question
        je_moja = otazka.created_by == request.user
        pouziva_nekto_iny = otazka.tests.exclude(id=test.id).exists()
        tq.mozem_upravit = je_moja and not pouziva_nekto_iny

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
            otazka = q_form.save(commit=False)
            otazka.created_by = request.user
            otazka.save()
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

@login_required
def prepni_stav_testu(request, test_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    
    test = get_object_or_404(Test, id=test_id)
    if request.method == 'POST':
        test.is_published = not test.is_published  # Preklopí hodnotu
        test.save()
        
    return redirect('detail_testu', test_id=test.id)

@login_required
def uprav_test(request, test_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    test = get_object_or_404(Test, id=test_id)
    
    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            return redirect('detail_testu', test_id=test.id)
    else:
        form = TestForm(instance=test)
    
    return render(request, 'quiz/vytvor_test.html', {'form': form, 'edit_mode': True, 'test': test})

@login_required
def spustit_test(request, test_id):
    test = get_object_or_404(Test, id=test_id, is_published=True)
    
    # 1. Kontrola, či už test nerobil
    if Result.objects.filter(user=request.user, test=test).exists():
        return redirect('dashboard')

    # Načítame otázky pre šablónu
    test_otazky = TestQuestion.objects.filter(test=test).select_related('question').order_by('order')

    if request.method == 'POST':
        celkove_body = 0
        ziskane_body = 0

        # Vytvoríme Result objekt
        vysledok = Result.objects.create(
            user=request.user,
            test=test,
            score=0,
            percentage=0
        )

        for tq in test_otazky:
            q = tq.question
            celkove_body += q.points
            
            # Získame dáta z formulára (name v HTML je "otazka_{{ otazka.id }}")
            field_name = f'otazka_{q.id}'
            
            if q.type == 'TXT':
                odpoved_text = request.POST.get(field_name, '').strip()
                
                # 1. Nájdeme správnu odpoveď v DB pre túto otázku, aby sme ju mohli previazať
                # (V modeli StudentResponse máš selected_answer ako ForeignKey na Answer)
                spravna_odpoved_obj = q.answers.filter(is_correct=True).first()
                
                # Ak študent niečo napísal, musíme to zaznamenať. 
                # Aby sme zachovali tvoj model, nájdeme odpoveď, ktorá sa zhoduje, 
                # alebo vytvoríme záznam o tom, čo napísal.
                
                # Hľadáme, či sa študent trafil do nejakej existujúcej možnosti
                najdena_odpoved = q.answers.filter(text__iexact=odpoved_text).first()
                
                if najdena_odpoved:
                    # Ak napísal niečo, čo je v zozname odpovedí (či už správne alebo nesprávne)
                    StudentResponse.objects.create(
                        result=vysledok, 
                        question=q, 
                        selected_answer=najdena_odpoved
                    )
                    if najdena_odpoved.is_correct:
                        ziskane_body += q.points
                else:
                    # Ak napísal niečo úplne iné (vždy nesprávne, lebo to nie je v DB)
                    # Vytvoríme "dočasnú" odpoveď v DB, aby sme ju mohli zobraziť vo výsledkoch
                    nova_neznama_odpoved = Answer.objects.create(
                        question=q, 
                        text=odpoved_text, 
                        is_correct=False
                    )
                    StudentResponse.objects.create(
                        result=vysledok, 
                        question=q, 
                        selected_answer=nova_neznama_odpoved
                    )

            elif q.type == 'SC':
                answer_id = request.POST.get(field_name)
                if answer_id:
                    odpoved = Answer.objects.filter(id=answer_id).first()
                    if odpoved:
                        StudentResponse.objects.create(result=vysledok, question=q, selected_answer=odpoved)
                        if odpoved.is_correct:
                            ziskane_body += q.points

            elif q.type == 'MC':
                selected_ids = request.POST.getlist(field_name)
                # Získame všetky správne odpovede pre túto otázku
                correct_answers = q.answers.filter(is_correct=True).values_list('id', flat=True)
                
                # Bodovanie MC: Študent musí označiť presne všetky správne (jednoduchá logika)
                if set(map(int, selected_ids)) == set(correct_answers):
                    ziskane_body += q.points
                
                # Uložíme každú zaškrtnutú odpoveď
                for aid in selected_ids:
                    odpoved = Answer.objects.filter(id=aid).first()
                    if odpoved:
                        StudentResponse.objects.create(result=vysledok, question=q, selected_answer=odpoved)

        # Finálny výpočet
        vysledok.score = ziskane_body
        vysledok.percentage = (ziskane_body / celkove_body * 100) if celkove_body > 0 else 0
        vysledok.save()

        return redirect('dashboard')

    # Pri GET požiadavke pošleme otázky do šablóny
    return render(request, 'quiz/spustit_test.html', {
        'test': test, 
        'otazky': [tq.question for tq in test_otazky] # Pošleme zoznam samotných otázok
    })
    
@login_required
def detail_vysledku(request, result_id):
    vysledok = get_object_or_404(Result, id=result_id, user=request.user)
    
    # Získame všetky odpovede študenta naraz
    odpovede_studenta = StudentResponse.objects.filter(result=vysledok).select_related('selected_answer')
    
    # Vytvoríme si mapu {question_id: selected_answer_object}
    mapa_odpovedi = {resp.question_id: resp.selected_answer for resp in odpovede_studenta}

    test_otazky = TestQuestion.objects.filter(test=vysledok.test).select_related('question').order_by('order')

    for tq in test_otazky:
        otazka = tq.question
        odpoved_obj = mapa_odpovedi.get(otazka.id) # Čo reálne študent "odovzdal"

        if otazka.type == 'TXT':
            if odpoved_obj:
                otazka.student_text = odpoved_obj.text
                otazka.is_correct_txt = odpoved_obj.is_correct
            else:
                otazka.student_text = "(žiadna)"
                otazka.is_correct_txt = False
        else:
            # Pre SC a MC (ideme cez všetky Answer otázky)
            vybrane_ids = odpovede_studenta.filter(question=otazka).values_list('selected_answer_id', flat=True)
            for ans in otazka.answers.all():
                ans.is_selected = ans.id in vybrane_ids

    return render(request, 'quiz/detail_vysledku.html', {
        'vysledok': vysledok,
        'test_otazky': test_otazky,
    })

@login_required
def vysledky_testu(request, test_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    
    test = get_object_or_404(Test, id=test_id)
    vysledky = Result.objects.filter(test=test).select_related('user__profil__trieda').order_by('-completed_at')
    
    trieda_filter = request.GET.get('trieda', '')
    hladaj_ziaka = request.GET.get('ziak', '')

    if trieda_filter:
        vysledky = vysledky.filter(user__profil__trieda__nazov=trieda_filter)
    
    if hladaj_ziaka:
        vysledky = vysledky.filter(user__username__icontains=hladaj_ziaka)

    triedy = Trieda.objects.filter(studenti__user__result__test=test).distinct()

    return render(request, 'quiz/vysledky_testu.html', {
        'test': test,
        'vysledky': vysledky,
        'triedy': triedy,
        'trieda_filter': trieda_filter,
        'hladaj_ziaka': hladaj_ziaka,
    })

@login_required
def uprav_otazku(request, question_id):
    if not is_teacher_or_staff(request.user):
        return redirect('index')
    
    otazka = get_object_or_404(Question, id=question_id, created_by=request.user)
    
    # Bezpecnostna kontrola - nepouziva ju nikto iny
    test_id = request.GET.get('test_id') or request.POST.get('test_id')
    if otazka.tests.exclude(id=test_id).exists():
        return redirect('dashboard')
    
    AnswerFormSet = formset_factory(AnswerForm, extra=0)
    existujuce_odpovede = otazka.answers.all()
    
    initial_data = [{'text': a.text, 'is_correct': a.is_correct} for a in existujuce_odpovede]

    if request.method == 'POST':
        q_form = QuestionForm(request.POST, instance=otazka)
        a_formset = AnswerFormSet(request.POST, prefix='odpovede', initial=initial_data)
        
        if q_form.is_valid() and a_formset.is_valid():
            q_form.save()
            # Zmaz stare odpovede a uloz nove
            otazka.answers.all().delete()
            for a_form in a_formset:
                if a_form.cleaned_data.get('text'):
                    Answer.objects.create(
                        question=otazka,
                        text=a_form.cleaned_data['text'],
                        is_correct=a_form.cleaned_data.get('is_correct', False),
                    )
            return redirect('detail_testu', test_id=test_id)
    else:
        q_form = QuestionForm(instance=otazka)
        a_formset = AnswerFormSet(prefix='odpovede', initial=initial_data)

    return render(request, 'quiz/uprav_otazku.html', {
        'q_form': q_form,
        'a_formset': a_formset,
        'otazka': otazka,
        'test_id': test_id,
    })