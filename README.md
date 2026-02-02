# Agent ATS — Twoja przepustka na rozmowę

Agent ATS to mini‑MVP, które porównuje CV z ogłoszeniem o pracę, wylicza wynik dopasowania i wskazuje brakujące słowa kluczowe. Projekt jest zrobiony tak, żeby robił efekt „wow” w kilkadziesiąt sekund podczas demo.

## Dlaczego to działa
- ATS odrzuca CV bez właściwych fraz z ogłoszenia.
- Kandydat nie wie, czego mu brakuje.
- Agent ATS pokazuje to od razu: wynik procentowy + konkretne słowa do dopisania.

## Demo w 30 sekund
1) Wrzuć CV (PDF/TXT) i wklej link do ogłoszenia.
2) Kliknij „Analizuj”.
3) Zobacz wynik i listę brakujących słów kluczowych.

## Funkcje
- Upload CV jako PDF/TXT.
- Link do ogłoszenia (preferowane) lub ręczne wklejenie treści.
- Wynik dopasowania z wizualnym paskiem.
- 3–5 brakujących słów kluczowych.
- Krótkie podsumowanie zmian.
- Gemini API + fallback heurystyczny (demo działa nawet bez klucza).

## Stos
- Python + Streamlit
- Gemini API (google‑generativeai)
- pypdf, requests

## Szybki start (lokalnie)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Konfiguracja (.env)

Utwórz plik `.env`:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

Jeśli klucz nie jest ustawiony, aplikacja użyje trybu heurystycznego.

## Docker

Build:

```bash
docker build -t agent-ats .
```

Run:

```bash
docker run --rm -p 8501:8501 --env-file .env agent-ats
```

## Prywatność
- Aplikacja nie zapisuje danych na dysku.
- Tekst CV i ogłoszenia jest przetwarzany wyłącznie w trakcie analizy.

## Autor
Stworzył to **Bartłomiej Marczuk** na potrzeby rekrutacji **JustJoin.it**.
