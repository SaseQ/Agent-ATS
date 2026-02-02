Kandydaci masowo wysyłają to samo CV na różne oferty i są odrzucani przez automaty (systemy ATS) jeszcze zanim rekruter na nie spojrzy.

Oto szczegóły projektu, który jest prosty w budowie (MVP), a robi świetne wrażenie podczas demo:

### Nazwa Projektu: **„Agent ATS: Twoja przepustka na rozmowę”**

#### 1. Konkretny problem kandydata
Kandydat ma świetne doświadczenie, ale jego CV nie zawiera specyficznych słów kluczowych z ogłoszenia o pracę (np. zamiast „zarządzanie zespołem” ma „team leadership”, a oferta wymaga polskiej frazy). Przez to system odrzuca go automatycznie. Kandydat nie wie, *dlaczego* nikt nie dzwoni.

#### 2. Rozwiązanie (Co robi Agent?)
Agent działa jako „Symulator rekrutera/ATS”.
1.  **Analizuje:** Pobiera treść CV (tekst/PDF) oraz treść ogłoszenia o pracę (link lub tekst).
2.  **Ocenia:** Wystawia „Dopasowanie procentowe” (np. 45%).
3.  **Naprawia:** Wypisuje 3-5 kluczowych brakujących umiejętności/słów, które *muszą* znaleźć się w CV, aby przejść sito.

#### 3. Dlaczego to jest "efektowne do pokazania"?
Ten projekt ma potężny **efekt „Wow” w 30 sekund**:
*   **Wizualizacja:** Możesz pokazać duży licznik (np. czerwone 30% -> zielone 95%).
*   **Natychmiastowa wartość:** Widownia od razu rozumie ból („Też tak miałem!”).
*   **Prostota:** Nie wymaga długiej interakcji (jak czat), wynik jest widoczny od razu po kliknięciu.

#### 4. Jak to zbudować (Prosty stos technologiczny)
*   **Interfejs (Frontend):** **Streamlit** (Python). Pozwala zbudować aplikację w 50 liniach kodu. Ma gotowe widżety do wgrania pliku i wyświetlania pasków postępu.
*   **Mózg (Backend):** Gemini API.
*   **Logika Agenta (Prompt):**
    > „Jesteś ekspertem ATS. Porównaj poniższe CV z ofertą pracy. 1. Podaj wynik dopasowania (0-100%). 2. Wypisz brakujące słowa kluczowe. 3. Podaj jedno zdanie podsumowania, co zmienić.”

### Przykład scenariusza demo:
1.  Pokazujesz na ekranie ofertę pracy (np. "Senior Java Developer").
2.  Wgrywasz przykładowe, słabe CV.
3.  Agent pokazuje wynik: **35% (Czerwony pasek)** i komunikat: *"Brakuje: Hibernate, Spring Boot, Microservices"*.
4.  Wklejasz poprawioną sekcję (lub Agent generuje sugestię).
5.  Wynik zmienia się na: **92% (Zielony pasek)**.
6.  *Efekt:* Publiczność widzi, jak AI „naprawiło” szanse kandydata.

To idealny projekt do portfolio – rozwiązuje palący problem, jest technicznie prosty (głównie inżynieria promptu), a wizualnie bardzo satysfakcjonujący. [linkedin](https://www.linkedin.com/pulse/phase-2-launching-careerai-develop-mvp-minimum-viable-santarovich-ygqhf)
