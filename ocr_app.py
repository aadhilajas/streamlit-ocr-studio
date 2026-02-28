import streamlit as st
import pytesseract
from PIL import Image
import json
import io
import base64
import time
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VisionText · OCR Studio",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root Variables ── */
:root {
    --ink: #0d0d0d;
    --paper: #f5f0e8;
    --cream: #ede8dc;
    --accent: #e85d26;
    --accent2: #2d6a4f;
    --gold: #c9a84c;
    --muted: #8a8070;
    --border: rgba(13,13,13,0.12);
    --card-bg: rgba(255,255,255,0.7);
    --shadow: 0 4px 32px rgba(13,13,13,0.10);
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper);
    color: var(--ink);
}

.main .block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1300px;
}

/* ── Header ── */
.ocr-header {
    display: flex;
    align-items: flex-end;
    gap: 1.2rem;
    margin-bottom: 0.3rem;
    padding-bottom: 1.2rem;
    border-bottom: 2px solid var(--ink);
}
.ocr-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    line-height: 1;
    color: var(--ink);
    letter-spacing: -1px;
}
.ocr-logo span {
    color: var(--accent);
}
.ocr-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.ocr-badge {
    display: inline-block;
    background: var(--accent2);
    color: #fff;
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    padding: 3px 9px;
    border-radius: 2px;
    text-transform: uppercase;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ── Cards ── */
.vision-card {
    background: var(--card-bg);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(8px);
    box-shadow: var(--shadow);
}
.card-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.6rem;
}

/* ── Upload Zone ── */
.stFileUploader > div {
    border: 2px dashed var(--border) !important;
    border-radius: 10px !important;
    background: rgba(245,240,232,0.5) !important;
    transition: all 0.2s;
}
.stFileUploader > div:hover {
    border-color: var(--accent) !important;
    background: rgba(232,93,38,0.04) !important;
}

/* ── Selectbox & Slider ── */
.stSelectbox [data-baseweb="select"] > div {
    background: white !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif;
}
.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: var(--accent) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em;
    background: var(--ink) !important;
    color: var(--paper) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.18s;
    box-shadow: 3px 3px 0 var(--accent) !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
    box-shadow: 3px 3px 0 var(--ink) !important;
    transform: translate(-1px,-1px);
}
.stButton > button:active {
    transform: translate(1px,1px);
    box-shadow: 1px 1px 0 var(--ink) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--cream);
    border-radius: 8px;
    padding: 3px;
    border: 1.5px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.05em;
    border-radius: 6px !important;
    padding: 0.45rem 1.2rem !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--ink) !important;
    box-shadow: 0 2px 8px rgba(13,13,13,0.10) !important;
}

/* ── Text area ── */
.stTextArea textarea {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    background: white !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--ink) !important;
}

/* ── JSON output ── */
.json-box {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    background: #0d0d0d;
    color: #e8e0d0;
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    white-space: pre-wrap;
    word-break: break-all;
    line-height: 1.7;
    border: 1.5px solid rgba(255,255,255,0.08);
    max-height: 460px;
    overflow-y: auto;
}
.json-key { color: #c9a84c; }
.json-str { color: #7ec8a0; }
.json-num { color: #e88a5d; }

/* ── Stats bar ── */
.stat-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0 0.3rem;
    flex-wrap: wrap;
}
.stat-chip {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    background: var(--cream);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    color: var(--muted);
    letter-spacing: 0.05em;
}
.stat-chip b { color: var(--ink); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--cream) !important;
    border-right: 1.5px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}

/* ── Alert / info ── */
.stAlert {
    border-radius: 8px !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Copy button ── */
.copy-btn {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    background: transparent;
    border: 1.5px solid var(--border);
    color: var(--muted);
    border-radius: 6px;
    padding: 3px 10px;
    cursor: pointer;
    transition: all 0.15s;
}
.copy-btn:hover { border-color: var(--accent); color: var(--accent); }

/* ── Progress ── */
.stProgress > div > div {
    background: var(--accent) !important;
}

/* ── Image display ── */
.stImage img {
    border-radius: 10px;
    border: 1.5px solid var(--border);
    box-shadow: var(--shadow);
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Hide Streamlit defaults ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--cream); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)


# ── Language Map ─────────────────────────────────────────────────────────────
LANGUAGES = {
    "English": "eng",
    "Arabic": "ara",
    "Bengali": "ben",
    "Chinese (Simplified)": "chi_sim",
    "Chinese (Traditional)": "chi_tra",
    "Dutch": "nld",
    "French": "fra",
    "German": "deu",
    "Greek": "ell",
    "Hebrew": "heb",
    "Hindi": "hin",
    "Indonesian": "ind",
    "Italian": "ita",
    "Japanese": "jpn",
    "Korean": "kor",
    "Malayalam": "mal",
    "Malay": "msa",
    "Marathi": "mar",
    "Persian": "fas",
    "Polish": "pol",
    "Portuguese": "por",
    "Russian": "rus",
    "Spanish": "spa",
    "Swedish": "swe",
    "Tamil": "tam",
    "Telugu": "tel",
    "Thai": "tha",
    "Turkish": "tur",
    "Urdu": "urd",
    "Vietnamese": "vie",
}

PSM_OPTIONS = {
    "Auto (full page)": 3,
    "Single column": 4,
    "Single block": 6,
    "Single line": 7,
    "Single word": 8,
    "Sparse text": 11,
    "Raw line": 13,
}

OEM_OPTIONS = {
    "Legacy Engine": 0,
    "LSTM Neural Net": 1,
    "Legacy + LSTM": 2,
    "Default": 3,
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def preprocess_image(img: Image.Image, scale: float, mode: str) -> Image.Image:
    w, h = img.size
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    if mode == "Grayscale":
        img = img.convert("L")
    elif mode == "Black & White":
        img = img.convert("L").point(lambda x: 255 if x > 128 else 0, "1")
    return img


def run_ocr(image: Image.Image, lang_codes: str, psm: int, oem: int) -> dict:
    config = f"--psm {psm} --oem {oem}"
    start = time.time()
    try:
        raw_text = pytesseract.image_to_string(image, lang=lang_codes, config=config)
        data = pytesseract.image_to_data(image, lang=lang_codes, config=config,
                                         output_type=pytesseract.Output.DICT)
        elapsed = time.time() - start

        # Build word-level details
        words = []
        for i, word in enumerate(data["text"]):
            if word.strip():
                words.append({
                    "word": word,
                    "confidence": int(data["conf"][i]),
                    "bbox": {
                        "x": data["left"][i], "y": data["top"][i],
                        "w": data["width"][i], "h": data["height"][i]
                    },
                    "block": data["block_num"][i],
                    "line": data["line_num"][i],
                })

        avg_conf = round(
            sum(w["confidence"] for w in words) / len(words), 1
        ) if words else 0.0

        return {
            "status": "success",
            "text": raw_text.strip(),
            "stats": {
                "characters": len(raw_text.strip()),
                "words": len(raw_text.split()),
                "lines": len([l for l in raw_text.splitlines() if l.strip()]),
                "avg_confidence": avg_conf,
                "processing_time_ms": round(elapsed * 1000, 1),
            },
            "settings": {
                "languages": lang_codes,
                "psm": psm,
                "oem": oem,
            },
            "words": words,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def colorize_json(obj: dict) -> str:
    raw = json.dumps(obj, indent=2, ensure_ascii=False)
    lines = []
    for line in raw.splitlines():
        # color keys
        import re
        line = re.sub(
            r'"([^"]+)"(\s*:)',
            r'<span class="json-key">"\1"</span>\2',
            line,
        )
        # color string values
        line = re.sub(
            r':\s*"([^"]*)"',
            lambda m: f': <span class="json-str">"{m.group(1)}"</span>',
            line,
        )
        # color numbers
        line = re.sub(
            r':\s*(-?\d+\.?\d*)',
            r': <span class="json-num">\1</span>',
            line,
        )
        lines.append(line)
    return "\n".join(lines)


def get_download_link(text: str, filename: str, label: str) -> str:
    b64 = base64.b64encode(text.encode()).decode()
    return (
        f'<a href="data:text/plain;base64,{b64}" download="{filename}" '
        f'style="font-family:\'DM Mono\',monospace;font-size:0.75rem;'
        f'color:#e85d26;text-decoration:none;border:1.5px solid #e85d26;'
        f'padding:4px 12px;border-radius:6px;transition:all 0.15s;">'
        f'⬇ {label}</a>'
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ocr-header">
    <div>
        <div class="ocr-logo">Vision<span>Text</span></div>
    </div>
    <div>
        <div class="ocr-tagline">OCR Studio &nbsp;·&nbsp; Multilingual &nbsp;·&nbsp; Offline</div>
        <span class="ocr-badge">✦ Powered by Tesseract</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="card-label">⬡ Configuration</div>', unsafe_allow_html=True)

    selected_langs = st.multiselect(
        "Languages",
        options=list(LANGUAGES.keys()),
        default=["English"],
        help="Select one or more languages present in the image.",
    )

    st.markdown("---")
    st.markdown('<div class="card-label">⬡ Engine Settings</div>', unsafe_allow_html=True)

    psm_choice = st.selectbox("Page Segmentation Mode", list(PSM_OPTIONS.keys()), index=0)
    oem_choice = st.selectbox("OCR Engine Mode", list(OEM_OPTIONS.keys()), index=3)

    st.markdown("---")
    st.markdown('<div class="card-label">⬡ Image Pre-Processing</div>', unsafe_allow_html=True)

    scale = st.slider("Upscale Factor", 0.5, 3.0, 1.0, 0.1,
                      help="Upscaling can improve accuracy on small text.")
    color_mode = st.selectbox("Color Mode", ["Original", "Grayscale", "Black & White"])

    st.markdown("---")
    st.markdown('<div class="card-label">⬡ Output</div>', unsafe_allow_html=True)
    show_word_data = st.checkbox("Include word-level data in JSON", value=False)

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#8a8070;line-height:1.8;">
    VisionText runs fully offline.<br>
    No data is sent to any server.<br><br>
    Install languages with:<br>
    <code style="background:#0d0d0d;color:#c9a84c;padding:2px 6px;border-radius:3px;">
    apt install tesseract-ocr-[lang]</code>
    </div>
    """, unsafe_allow_html=True)


# ── Main Layout ───────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown('<div class="card-label">⬡ Image Input</div>', unsafe_allow_html=True)

    upload_tab, paste_tab = st.tabs(["  Upload File  ", "  Paste URL / Path  "])

    uploaded_file = None
    image = None

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Drop an image here",
            type=["png", "jpg", "jpeg", "bmp", "tiff", "tif", "webp", "gif"],
            label_visibility="collapsed",
        )

    with paste_tab:
        url_input = st.text_input(
            "Image path or URL",
            placeholder="e.g. /home/user/image.png",
            label_visibility="collapsed",
        )
        if url_input:
            try:
                if url_input.startswith("http"):
                    import urllib.request
                    with urllib.request.urlopen(url_input) as resp:
                        image = Image.open(io.BytesIO(resp.read()))
                else:
                    image = Image.open(url_input)
            except Exception as e:
                st.error(f"Could not load image: {e}")

    if uploaded_file:
        image = Image.open(uploaded_file)

    if image:
        proc_image = preprocess_image(image.copy(), scale, color_mode)
        st.image(proc_image, use_container_width=True, caption="Preview")
        w, h = image.size
        st.markdown(
            f'<div class="stat-row">'
            f'<span class="stat-chip"><b>{w}×{h}</b> px</span>'
            f'<span class="stat-chip"><b>{image.mode}</b> color</span>'
            f'<span class="stat-chip"><b>{color_mode}</b> mode</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


with right_col:
    st.markdown('<div class="card-label">⬡ Extracted Text</div>', unsafe_allow_html=True)

    extract_btn = st.button("⌁ Extract Text", use_container_width=True, type="primary")
    result = None

    if "ocr_result" not in st.session_state:
        st.session_state.ocr_result = None

    if extract_btn:
        if not image:
            st.warning("Please upload or load an image first.")
        elif not selected_langs:
            st.warning("Select at least one language.")
        else:
            lang_codes = "+".join(LANGUAGES[l] for l in selected_langs)
            psm_val = PSM_OPTIONS[psm_choice]
            oem_val = OEM_OPTIONS[oem_choice]
            proc_image = preprocess_image(image.copy(), scale, color_mode)

            with st.spinner("Extracting text…"):
                st.session_state.ocr_result = run_ocr(proc_image, lang_codes, psm_val, oem_val)

    result = st.session_state.ocr_result

    if result:
        if result["status"] == "error":
            st.error(f"OCR Error: {result['message']}")
            st.info(
                "Make sure Tesseract is installed and the selected language "
                "packs are available. Install a language pack with:\n"
                "`sudo apt install tesseract-ocr-[lang_code]`"
            )
        else:
            stats = result["stats"]
            st.markdown(
                f'<div class="stat-row">'
                f'<span class="stat-chip">⏱ <b>{stats["processing_time_ms"]} ms</b></span>'
                f'<span class="stat-chip">✦ <b>{stats["avg_confidence"]}%</b> confidence</span>'
                f'<span class="stat-chip">📄 <b>{stats["words"]}</b> words</span>'
                f'<span class="stat-chip">↵ <b>{stats["lines"]}</b> lines</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            text_tab, json_tab = st.tabs(["  Plain Text  ", "  JSON View  "])

            with text_tab:
                edited = st.text_area(
                    "Extracted text (editable)",
                    value=result["text"],
                    height=360,
                    label_visibility="collapsed",
                )
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.markdown(
                        get_download_link(edited, "extracted_text.txt", "Download .txt"),
                        unsafe_allow_html=True,
                    )

            with json_tab:
                output_obj = {
                    "status": result["status"],
                    "text": result["text"],
                    "stats": result["stats"],
                    "settings": result["settings"],
                }
                if show_word_data:
                    output_obj["words"] = result["words"]

                json_str = json.dumps(output_obj, indent=2, ensure_ascii=False)

                st.markdown(
                    f'<div class="json-box">{colorize_json(output_obj)}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    get_download_link(json_str, "ocr_result.json", "Download .json"),
                    unsafe_allow_html=True,
                )
    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem;color:#8a8070;">
            <div style="font-size:3rem;margin-bottom:1rem;">◈</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
            color:#0d0d0d;margin-bottom:0.4rem;">No extraction yet</div>
            <div style="font-family:'DM Mono',monospace;font-size:0.75rem;letter-spacing:0.05em;">
            Upload an image and press Extract Text
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
font-family:'DM Mono',monospace;font-size:0.65rem;color:#8a8070;
letter-spacing:0.08em;padding:0.3rem 0;">
    <span>VisionText OCR Studio &nbsp;·&nbsp; Fully Offline</span>
    <span>Tesseract &amp; Streamlit</span>
</div>
""", unsafe_allow_html=True)
