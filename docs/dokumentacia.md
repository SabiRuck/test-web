# Kompletná technická dokumentácia projektu: EduApp
**Názov zadania:** Webová aplikácia „Správa školských testov a otázok“ (Zadanie 7)  
**Trieda:** 3.AT  
**Autori:** Sabína Rucková (Backend, Logika & Deployment) & Petra Školová (Frontend, UI/UX & Dokumentácia)  
**Školský rok:** 2025/2026  

## 1. Úvod a cieľ projektu
Projekt **EduApp** (v systéme registrovaný ako projekt `test-web` s aplikáciou `quiz`) vznikol ako finálne zadanie v rámci 3. ročníka strednej školy v odbore Inteligentné technológie. Hlavným cieľom bolo navrhnúť, naimplementovať a úspešne online nasadiť webovú aplikáciu pre učiteľov na tvorbu a správu testov, otázok a na evidenciu výsledkov žiakov. 

Projekt simuluje reálne školské prostredie, v ktorom učiteľ vystupuje ako správca obsahu a študent ako používateľ, ktorý testy vypĺňa a okamžite získava spätnú väzbu o svojej úspešnosti.

## 2. Architektúra systému a databázový model 
Aplikácia využíva silný backend framework **Django (Python)** postavený na architektúre **MVT (Model-View-Template)**. Ako lokálne úložisko dát počas vývoja slúži relačná databáza **SQLite3** (`db.sqlite3`).

### 2.1 Štruktúra databázových modelov (`models.py`)
Podľa presných požiadaviek zadania boli navrhnuté a zmigrované nasledujúce entity:

1. **Test**
   - `nazov` (CharField): Jednoznačné pomenovanie testu.
   - `popis` (TextField): Pokyny a inštrukcie pre študentov pred spustením.
   - `predmet` (CharField): Školský predmet (slúži na kategorizáciu a filtrovanie).
   - `casovy_limit` (IntegerField): Čas vyhradený na test v minútach.
   - `publikovany` (BooleanField): Príznak určujúci, či je test viditeľný pre študentov.

2. **Question (Otázka)**
   - `text_otazky` (TextField): Znenie otázky.
   - `typ_otazky` (CharField): Typ zadania (napr. výber jednej možnosti / viacero odpovedí).
   - `pocet_bodov` (IntegerField): Váha danej otázky.

3. **Answer (Odpoveď)**
   - `text_odpovede` (CharField): Textové znenie alternatívy.
   - `spravna` (BooleanField): Logická hodnota určujúca správnosť odpovede.
   - `otazka` (ForeignKey): Väzba typu 1:N smerujúca na model `Question`.

4. **Result (Výsledok)**
   - `pouzivatel` (ForeignKey): Prepojenie na vstavaný Django autentifikačný model používateľa (`User`).
   - `test` (ForeignKey): Väzba na absolvovaný test.
   - `ziskane_body` (IntegerField): Suma dosiahnutých bodov.
   - `percenta` (DecimalField): Percentuálna úspešnosť výpočtu.
   - `datum_vyplnenia` (DateTimeField): Presný časový odtlačok uloženia výsledku.

### 2.2 Povinný vzťah Many-to-Many (M:N)
Medzi entitami `Test` a `Question` existuje povinný vzťah **M:N**, realizovaný prostredníctvom asociačného modelu **`TestQuestion`**. Tento prístup zabezpečuje, že jedna otázka môže byť nezávisle recyklovaná a použitá vo viacerých testoch súčasne, pričom si uchováva informáciu o svojom poradí či špecifickom bodovaní v konkrétnom teste.

Tu je kompletne rozpísaný a detailne rozpracovaný **Bod 3: Backendová logika a funkcionality (Práca Študenta A)**. Je napísaný presne v takom štýle, aby zapadol do zvyšku tvojej správy, a priamo obsahuje reálne názvy vášho projektu a aplikácie (`test-web`, `quiz`), prihlasovacie údaje používateľov z vašich poznámok (`hanka`, `janko`, `igorko`) a presnú logiku filtrov a modelov, ktoré ste naprogramovali.

## 3. Backendová logika a funkcionality (Práca Študenta A)
Backendová časť systému bola vyvinutá v prostredí Django (architektúra projektu `test-web` a core aplikácie `quiz`) s cieľom zabezpečiť spoľahlivé spracovanie biznis logiky, validáciu vstupov, bezpečné ukladanie citlivých údajov do relačnej databázy a plynulé poskytovanie dynamických dát pre frontend.

### 3.1 Autentifikácia, autorizácia a správa používateľských rolí
Systém využíva vstavaný autentifikačný modul `django.contrib.auth`. Prístupové práva sú striktne rozdelené na základe dvoch klientskych rolí, pričom pre potreby testovania a prezentácie boli v systéme vytvorené fixné kontá:

1. **Rola: Učiteľ / Administrátor (Používateľ `hanka`)**
   - Má plné oprávnenie na správu obsahu (CRUD operácie) nad modelmi `Test`, `Question` a `Answer`.
   - Disponuje prístupom do hlavného Dashboardu učiteľa, kde vidí globálny zoznam všetkých testov (publikovaných aj rozpracovaných).
   - Má exkluzívne právo prezerať modul výsledkov, kde systém zobrazuje úspešnosť všetkých žiakov.

2. **Rola: Študent (Používatelia `janko`, `igorko`)**
   - Po overení mena a hesla je študent presmerovaný na študentské rozhranie.
   - Systém prostredníctvom podmienky v databázovom dopyte (`Test.objects.filter(publikovany=True)`) zabezpečuje, že študent vidí výhradne testy schválené na vypĺňanie. Rozpracované testy sú preňho neviditeľné.
   - Študent nemá prístup k editácii otázok ani k výsledkom iných žiakov.

### 3.2 Implementácia CRUD operácií a správa testovacej bázy
- Pre učiteľa bolo implementované kompletné administračné rozhranie priamo vo webe (oddelené od Django Admina), ktoré spracováva nasledovné scenáre:
- **Tvorba a mazanie testu:** Spracovanie formulárov na definovanie základných parametrov testu (názov, popis, časový limit, priradenie predmetu). Implementované je aj bezpečné mazanie testu vrátane kaskádového čistenia väzieb.
- **Banka otázok:** Samostatný modul, ktorý funguje ako úložisko všetkých otázok naprieč predmetmi. Učiteľ môže vytvárať nové otázky s ľubovoľným počtom odpovedí.
- **Priraďovanie otázok do testu:** Využitie asociačného modelu `TestQuestion`. Učiteľ môže otvoriť existujúci test a pridávať doň otázky z globálnej banky. V tomto kroku backend ukladá aj dodatočné informácie, ako je poradie otázky v danom teste a jej bodová váha pre konkrétny test.

### 3.3 Logika spracovania POST requestu a vyhodnocovanie testu
Najkritickejšou backendovou operáciou z hľadiska logiky je spracovanie a vyhodnotenie vyplneného testu. Tento proces prebieha plne na strane servera, čím sa predchádza manipulácii s výsledkami na strane klienta:

1. **Odoslanie formulára:** Keď študent (alebo vypršanie časomiery cez JavaScript) odošle test, prehliadač vygeneruje `POST` požiadavku, ktorá obsahuje ID testu a zoznam zakliknutých ID odpovedí (z `input type="radio"` alebo `checkbox`).
2. **Backendová validácia:** View zachytí `request.POST`. Následne z databázy vytiahne všetky správne odpovede naviazané na otázky daného testu (`Answer.objects.filter(otazka__in=..., spravna=True)`).
3. **Výpočet úspešnosti:** Algoritmus prejde cyklom cez odpovede študenta. Za každú zhodu so správnou odpoveďou pripočíta body prislúchajúce danej otázke.
4. **Zápis výsledku (Model `Result`):** Po sčítaní bodov backend vypočíta finálnu percentuálnu úspešnosť. Tieto dáta spolu s ID študenta, ID testu a aktuálnym časovým odtlačkom servera (`timezone.now()`) zapíše ako nový riadok do tabuľky `Result`. Študentovi je následne okamžite vyrenderovaná šablóna s jeho dosiahnutým výsledkom.

### 3.4 Vyhľadávanie, filtrovanie a agregácia dát
Aby bola aplikácia prehľadná aj pri väčšom množstve dát, bolo implementované dynamické filtrovanie prostredníctvom `request.GET` parametrov v URL adrese:

- **Filtrovanie podľa publikácie (Učiteľ):** Učiteľ si môže na svojom dashboarde jedným kliknutím vyfiltrovať iba testy, ktoré sú rozpracované (archív), alebo iba tie, ktoré sú aktuálne zverejnené a spustené pre žiakov.
- **Filtrovanie podľa predmetu (Študent):** Na študentskej nástenke bol vytvorený filter, ktorý podľa zvoleného predmetu (napr. Matematika, Elektronika, Sieťové technológie) okamžite zúži zoznam zobrazených testov, čo uľahčuje navigáciu.
- **Vyhľadávanie výsledkov:** V učiteľskom prehľade úspešnosti bol integrovaný vyhľadávací filter. Učiteľ môže do vyhľadávacieho poľa zadať meno žiaka (napr. `janko`) alebo konkrétnu triedu (napr. `3.AT`), pričom backend vykoná dopyt s podmienkou `__icontains` a vráti očistenú tabuľku s filtrami na mieru.

## 4. Architektúra frontendu a UI/UX (Práca Študenta B)
Hlavným cieľom frontendovej refaktorizácie bolo premeniť strohé a nezarovnané HTML šablóny na moderné, reprezentatívne a čisté prostredie.

### 4.1 Typografia a globálna stabilizácia vzhľadu
- **Moderné písmo:** Pomocou `@import` bolo implementované prémiové bezpätkové písmo **Plus Jakarta Sans**, ktoré radikálne zlepšilo čitateľnosť textových údajov.
- **Reset dedičnosti štýlov:** Na zamedzenie nežiaduceho dedenia centrovania z hlavných elementov bol vytvorený striktný reset, ktorý vracia zarovnanie textov, tabuliek a formulárov doľava:

  body, .content, .container {
      text-align: left !important;
  }
  h1, h2, h3, p, table, tr, td, th, form, div {
      text-align: left !important;
  }

### 4.2 Stabilizácia navigácie a Pixel-Perfect zarovnanie
Horná navigačná lišta (`<nav>`) prešla kompletným redizajnom postaveným na **CSS Flexboxe** (`display: flex !important; justify-content: space-between !important;`). Vďaka tomu je logo a odkaz na Dashboard fixne umiestnené vľavo a používateľské menu vpravo.

V pôvodnom návrhu odhlasovacie tlačidlo vyskakovalo mimo vertikálnej osi riadku. Tento vizuálny nedostatok bol odstránený aplikovaním presnej 2-pixelovej relatívnej transformácie na stred:

.btn-logout {
    display: inline-flex !important;
    align-items: center !important;
    line-height: 1 !important;
    transform: translateY(2px) !important; /* Odstránenie výškového skoku */
}

### 4.3 Mikro-interakcie a efekty neónového svietenia (Glow Effects)
Aplikácia využíva moderné dynamické stavy `:hover` s plynulým prechodom (`transition: all 0.2s ease-in-out`), ktoré dávajú používateľovi okamžitú spätnú väzbu:

* **Odkaz Dashboard / EduApp:** Pri prechode kurzorom sa aktivuje jemné svetlofialové pozadie (`var(--primary-light)`) so zaoblením a elegantným difúznym tieňom ladiacim s identitou webu.
* **Tlačidlo Odhlásiť sa:** Z dôvodu varovného charakteru akcie bol pre toto tlačidlo navrhnutý unikátny stav – text aj pozadie sa rozsvietia do **striktnej červenej farby** doplnenej o výrazný neónový glow efekt tieňa:

.btn-logout:hover {
    color: var(--danger) !important;
    background-color: var(--danger-bg) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.5) !important; /* Červená žiara */
    transform: translateY(2px) !important;
}

### 4.4 Sémantické farebné kódovanie tlačidiel úloh
Aby mal učiteľ na hlavnej stránke okamžitý prehľad, spodné akčné tlačidlá pod tabuľkou boli farebne diverzifikované. Na úspešné prebitie pôvodných inline štýlov z HTML kódu boli použité pokročilé atribútové CSS selektory:

* **Banka otázok (Zelená):** `a[href*="banka_otazok"] button` prechádza na zelenú farbu úspechu `#10b981`.
* **Nastavenia testu (Žltá):** `a[href*="uprav_test"] button` evokuje konfiguráciu prostredníctvom žltej farby `#f59e0b`.
* **Výsledky testu (Tyrkysová):** `a[href*="vysledky_testu"] button` využíva informačnú modrú farbu `#17a2b8`.

## 5. Produkčné nasadenie a testovanie (Spoločný 5. Týždeň)
Piaty týždeň vývojového cyklu bol zameraný na presun aplikácie z lokálneho prostredia na internet a finálnu elimináciu chýb.

### 5.1 Nasadenie na cloud (Študent A)
Projekt bol úspešne nakonfigurovaný a nasadený na bezplatnú hostingovú platformu (Render.com / Railway.app). Pre bezproblémový online beh boli implementované kľúčové produkčné technológie:

* **WhiteNoise:** Django knižnica zabezpečujúca, že statické súbory (najmä upravené CSS štýly a písma) sú bezpečne a rýchlo distribuované priamo aplikáciou bez potreby zložitej konfigurácie externých webových serverov.
* **Gunicorn:** Nasadenie produkčného WSGI HTTP servera zabezpečujúceho stabilitu a podporu viacerých dopytov súčasne.

### 5.2 Výkonnostný Bug Hunting na produkcii (Študent B)
Po nasadení aplikácie online prebehlo intenzívne spoločné testovanie. Z pohľadu frontendu boli vyriešené dva závažné problémy:

1. **Zalamovanie prvkov:** Pri menších rozlíšeniach obrazoviek prichádzalo k zalamovaniu navigačného panela do dvoch riadkov. Problém bol eliminovaný deklaráciou `white-space: nowrap !important;` na pravom bloku `.nav-links`.
2. **Problémy s vyrovnávacou pamäťou (Cache):** Novo nasadené CSS štýly sa na produkčnom servery na niektorých zariadeniach hneď neprejavili z dôvodu starej cache prehliadača. Chyba bola odstránená vynúteným znovunačítaním cez **`CTRL + F5`**.

## 6. Záver
Projekt **EduApp** úspešne splnil všetky stanovené body zadania. Výsledkom spolupráce je plne funkčný, databázovo prepojený systém na správu testov so stabilným backendom, čistým moderným frontendom s pokročilými interaktívnymi prvkami a úspešným online nasadením. Kompletné zdrojové kódy a táto sprievodná dokumentácia sú bezpečne publikované v Git repozitári.