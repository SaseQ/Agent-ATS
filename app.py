import html
import json
import os
import re
from typing import List, Tuple

import streamlit as st
import requests
from pypdf import PdfReader

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

DEFAULT_GEMINI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


def resolve_gemini_settings() -> Tuple[str, str, bool]:
    api_key = os.getenv("GEMINI_API_KEY", DEFAULT_GEMINI_API_KEY).strip()
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    has_key = bool(api_key) and api_key != DEFAULT_GEMINI_API_KEY
    return api_key, model_name, has_key


MAX_CHARS = 12000

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "that", "the", "this", "to", "was",
    "were", "with", "you", "your", "our", "we", "they", "their", "them", "i", "me",
    "my", "he", "she", "his", "her", "not", "but", "if", "then", "than", "so", "do",
    "does", "did", "done", "can", "could", "should", "would", "will", "just", "into",
    "about", "over", "under", "also", "such", "other", "more", "most", "less", "least",
    "up", "down", "out", "off", "no", "yes", "may", "might", "must", "within",
    "plus", "using", "use", "used", "via", "per", "etc"
}


def trim_text(text: str, max_chars: int = MAX_CHARS) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        parts.append(page_text)
    return "\n".join(parts).strip()


def extract_text_from_upload(uploaded_file) -> str:
    name = (uploaded_file.name or "").lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    if name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8", errors="ignore").strip()
    return ""


def fetch_job_text(url: str) -> str:
    headers = {"User-Agent": "AgentATS/1.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    text = response.text
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+.#-]{2,}", text.lower())


def top_keywords(text: str, limit: int = 20) -> List[str]:
    counts = {}
    for token in tokenize(text):
        if token in STOPWORDS:
            continue
        counts[token] = counts.get(token, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return [word for word, _ in ranked[:limit]]


def heuristic_analysis(cv_text: str, job_text: str) -> Tuple[int, List[str], str]:
    keywords = top_keywords(job_text, limit=20)
    if not keywords:
        return 0, [], "Opis ogłoszenia jest zbyt krótki, aby wyciągnąć słowa kluczowe."
    cv_lower = cv_text.lower()
    present = [kw for kw in keywords if kw in cv_lower]
    missing = [kw for kw in keywords if kw not in cv_lower][:5]
    score = int(round(100 * len(present) / len(keywords)))
    summary = "Dodaj brakujące słowa kluczowe z ogłoszenia do CV."
    return score, missing, summary


def build_prompt(cv_text: str, job_text: str) -> str:
    return (
        "You are an ATS expert. Compare the CV and the job description. "
        "Return ONLY valid JSON with keys: "
        "score (integer 0-100), "
        "missing_keywords (array of 3 to 5 strings), "
        "summary (one sentence, max 30 words, in Polish language). "
        "No extra text.\n\n"
        f"CV:\n{cv_text}\n\n"
        f"JOB:\n{job_text}\n"
    )


def parse_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def gemini_analysis(cv_text: str, job_text: str, api_key: str, model_name: str) -> Tuple[int, List[str], str]:
    if genai is None:
        raise RuntimeError("google-generativeai is not installed")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    prompt = build_prompt(cv_text, job_text)
    response = model.generate_content(prompt)
    data = parse_json(response.text)
    score = int(data.get("score", 0))
    score = max(0, min(100, score))
    missing = data.get("missing_keywords", [])
    if not isinstance(missing, list):
        missing = []
    missing = [str(item).strip() for item in missing if str(item).strip()]
    summary = str(data.get("summary", "")).strip()
    return score, missing[:5], summary


if load_dotenv is not None:
    load_dotenv()

st.set_page_config(page_title="Agent ATS", page_icon="A", layout="centered")

api_key, model_name, use_gemini = resolve_gemini_settings()

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --bg: #0b1116;
  --bg-alt: #101820;
  --card: #121b24;
  --ink: #e6edf3;
  --muted: #9aa6b2;
  --accent: #22c55e;
  --accent-2: #38bdf8;
  --accent-3: #f59e0b;
  --shadow: 0 18px 45px rgba(2, 6, 23, 0.45);
  --radius: 18px;
}

html, body, [class*="css"] {
  font-family: 'Instrument Sans', 'Space Grotesk', ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  color: var(--ink);
}

.stApp {
  background: radial-gradient(circle at 10% 10%, #0f1720 0%, #0b1116 55%, #0b1116 100%);
}

[data-testid="stAppViewContainer"] .main,
[data-testid="stAppViewContainer"] .main > div,
[data-testid="stAppViewContainer"] .main .block-container,
[data-testid="stAppViewContainer"] section.main > div {
  padding-top: 1.5rem;
  padding-bottom: 4rem;
  max-width: 1280px !important;
  width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

.hero {
  position: relative;
  overflow: hidden;
  border-radius: 26px;
  padding: 1.8rem 2rem;
  background: linear-gradient(135deg, #121b24 0%, #141f2a 55%, #1a2430 100%);
  box-shadow: var(--shadow);
  border: 1px solid rgba(56, 189, 248, 0.18);
}

.hero h1 {
  font-family: 'Space Grotesk', 'Instrument Sans', sans-serif;
  font-size: clamp(1.8rem, 2.5vw, 2.6rem);
  margin: 0 0 0.4rem 0;
  letter-spacing: -0.02em;
}

.hero p {
  margin: 0.2rem 0 0 0;
  color: var(--muted);
  font-size: 1.02rem;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.16);
  color: #86efac;
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.6rem;
}

.mode-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.18);
  color: #bae6fd;
  font-weight: 600;
  font-size: 0.78rem;
  margin-top: 0.7rem;
}

.orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(0px);
  opacity: 0.45;
  z-index: 0;
}

.orb.one {
  width: 120px;
  height: 120px;
  right: -30px;
  top: -20px;
  background: radial-gradient(circle at 30% 30%, #38bdf8 0%, rgba(56, 189, 248, 0) 70%);
}

.orb.two {
  width: 160px;
  height: 160px;
  right: 40px;
  bottom: -70px;
  background: radial-gradient(circle at 40% 40%, #22c55e 0%, rgba(34, 197, 94, 0) 70%);
}

.section-title {
  margin: 1.6rem 0 0.6rem 0;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  font-weight: 600;
}

.card {
  background: var(--card);
  border-radius: var(--radius);
  padding: 1.2rem 1.4rem;
  box-shadow: var(--shadow);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.card-title {
  font-weight: 700;
  margin-bottom: 0.6rem;
  font-size: 1.05rem;
}

.score-row {
  display: flex;
  align-items: baseline;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.score {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.score-label {
  color: var(--muted);
  font-weight: 600;
}

.score-bar {
  width: 100%;
  height: 10px;
  background: #1f2a37;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 0.8rem;
}

.score-bar span {
  display: block;
  height: 100%;
  border-radius: 999px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.chip {
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.2);
  color: #bae6fd;
  font-weight: 600;
  font-size: 0.85rem;
}

.reveal {
  animation: slideUp 0.6s ease both;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  border-radius: 14px !important;
  border: 1px solid #2b3846 !important;
  background: #0f1720 !important;
  color: var(--ink) !important;
  box-shadow: inset 0 1px 0 rgba(15, 23, 42, 0.4);
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent-2) !important;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
}

[data-testid="stFileUploader"] {
  border: 2px dashed #2b3846;
  padding: 0.9rem;
  border-radius: 16px;
  background: #0f1720;
}

.stButton > button {
  background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
  color: white !important;
  border: none !important;
  border-radius: 999px !important;
  padding: 0.75rem 1.8rem !important;
  font-weight: 700 !important;
  box-shadow: 0 14px 30px rgba(34, 197, 94, 0.18);
}

.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 32px rgba(34, 197, 94, 0.26);
}

.stButton > button:active {
  transform: translateY(0);
}

.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: var(--muted) !important;
  border: 1px solid #2b3846 !important;
  box-shadow: none !important;
}

.stButton > button[kind="secondary"]:hover {
  color: var(--ink) !important;
  border-color: #3b4958 !important;
}

[data-testid="stHorizontalBlock"] {
  flex-direction: column !important;
  gap: 1.2rem;
}

[data-testid="stColumn"] {
  width: 100% !important;
  flex: 1 1 100% !important;
}

.hero {
  padding: 1.4rem 1.4rem;
}

.score {
  font-size: 2.4rem;
}
</style>
""",
    unsafe_allow_html=True,
)

mode_label = "Tryb Gemini AI" if use_gemini else "Tryb heurystyczny"

st.markdown(
    f"""
<div class="hero reveal">
  <div class="orb one"></div>
  <div class="orb two"></div>
  <div class="hero-badge">Agent ATS</div>
  <h1>Podbij skuteczność CV w ATS</h1>
  <p>Wrzuć CV i link do ogłoszenia. Zobacz wynik dopasowania i brakujące słowa kluczowe.</p>
  <div class="mode-pill">{mode_label}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div style="height: 2.4rem;"></div>
<div style="text-align:center; color: var(--muted); font-size: 0.85rem;">
  Stworzył to Bartłomiej Marczuk na potrzeby rekrutacji JustJoin.it
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Wejścia</div>', unsafe_allow_html=True)

if "show_manual_inputs" not in st.session_state:
    st.session_state.show_manual_inputs = False

def toggle_manual_inputs() -> None:
    st.session_state.show_manual_inputs = not st.session_state.show_manual_inputs

toggle_label = (
    "Pokaż ręczne pola tekstowe"
    if not st.session_state.show_manual_inputs
    else "Ukryj ręczne pola tekstowe"
)
st.button(toggle_label, type="secondary", on_click=toggle_manual_inputs, key="toggle_manual_inputs")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card-title">CV</div>', unsafe_allow_html=True)
    cv_file = st.file_uploader("Dodaj plik CV (PDF lub TXT)", type=["pdf", "txt"])
    if st.session_state.show_manual_inputs:
        cv_text = st.text_area("...albo wklej treść CV", height=220)
    else:
        cv_text = ""

with col2:
    st.markdown('<div class="card-title">Ogłoszenie</div>', unsafe_allow_html=True)
    job_url = st.text_input("Link do ogłoszenia (preferowane)")
    if st.session_state.show_manual_inputs:
        job_text = st.text_area("Wklej treść ogłoszenia", height=220)
    else:
        job_text = ""

analyze = st.button("Analizuj", type="primary", use_container_width=True)

if analyze:
    errors = []

    cv_payload = ""
    if cv_file is not None:
        try:
            cv_payload = extract_text_from_upload(cv_file)
        except Exception as exc:
            errors.append(f"Nie udało się odczytać pliku CV: {exc}")
    if not cv_payload:
        cv_payload = cv_text.strip()

    job_payload = job_text.strip()
    if not job_payload and job_url.strip():
        try:
            job_payload = fetch_job_text(job_url.strip())
        except Exception as exc:
            errors.append(f"Nie udało się pobrać ogłoszenia z linku: {exc}")

    if not cv_payload:
        errors.append("Dodaj plik CV lub wklej treść CV.")
    if not job_payload:
        errors.append("Podaj link do ogłoszenia lub wklej jego treść.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        cv_payload = trim_text(cv_payload)
        job_payload = trim_text(job_payload)

        with st.spinner("Analyzing..."):
            try:
                if use_gemini and api_key:
                    score, missing, summary = gemini_analysis(
                        cv_payload, job_payload, api_key, model_name
                    )
                else:
                    score, missing, summary = heuristic_analysis(cv_payload, job_payload)
            except Exception as exc:
                st.error(f"Analiza nie powiodła się: {exc}")
                st.stop()

        color = "#2ecc71" if score >= 75 else "#f39c12" if score >= 50 else "#e74c3c"

        st.markdown('<div class="section-title">Wyniki</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="card reveal">
  <div class="card-title">Wynik dopasowania</div>
  <div class="score-row">
    <div class="score" style="color:{color};">{score}%</div>
    <div class="score-label">Dopasowanie ATS</div>
  </div>
  <div class="score-bar"><span style="width:{score}%; background:{color};"></span></div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        if missing:
            chips = "".join(
                f"<span class='chip'>{html.escape(item)}</span>" for item in missing
            )
            st.markdown(
                f"""
<div class="card reveal">
  <div class="card-title">Brakujące słowa kluczowe</div>
  <div class="chip-row">{chips}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
<div class="card reveal">
  <div class="card-title">Brakujące słowa kluczowe</div>
  <p>Brak brakujących słów kluczowych.</p>
</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        summary_text = html.escape(summary or "Brak podsumowania.")
        st.markdown(
            f"""
<div class="card reveal">
  <div class="card-title">Podsumowanie</div>
  <p>{summary_text}</p>
</div>
""",
            unsafe_allow_html=True,
        )

        with st.expander("Inputs used"):
            st.write(f"CV chars: {len(cv_payload)}")
            st.write(f"Job chars: {len(job_payload)}")
