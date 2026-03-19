import streamlit as st
import random
import httpx
from datetime import datetime

st.set_page_config(page_title="Surgical Video Evaluation", layout="wide", page_icon="🏥")

SUPABASE_URL = "https://jkfdxwhusxpfojvsqtlv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprZmR4d2h1c3hwZm9qdnNxdGx2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4ODI4MjMsImV4cCI6MjA4OTQ1ODgyM30.0oUmlIWgCbVjK2Yqne6AnGiEd3LoqIhucmnGTxFJ5-U"

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f0f4f8; }
.header-bar { background: linear-gradient(90deg,#1e3a5f,#2563eb); padding:14px 24px; border-radius:10px;
               color:white; display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.vid-label { text-align:center; font-weight:700; font-size:1.1rem; padding:6px;
              border-radius:6px; margin-bottom:6px; }
.lbl-a { background:#dbeafe; color:#1e40af; }
.lbl-b { background:#dcfce7; color:#166534; }
.rating-header { display:grid; grid-template-columns:2fr 1fr 1fr;
                  gap:8px; font-weight:700; font-size:0.85rem; color:#475569;
                  padding:6px 10px; border-bottom:2px solid #e2e8f0; margin-bottom:4px; }
div[data-testid="stForm"] { background:white; padding:16px; border-radius:10px;
                              box-shadow:0 1px 4px rgba(0,0,0,0.08); }
</style>
""", unsafe_allow_html=True)

VIDEOS = {
    "Blood_Sucking_100813_VID005": {"original": "https://drive.google.com/file/d/156hCT5sOOGlVZZ9bHGN-3SaaAIjqQcSP/preview", "inpainted": "https://drive.google.com/file/d/1W4K2ynUwbfEuDDsboImOqQKv4j1KUYDM/preview", "category": "Blood Sucking"},
    "Bleeding_100813_VID005": {"original": "https://drive.google.com/file/d/1nhchHUosO-Apkgf7ResMkNOK0BuRyZJ6/preview", "inpainted": "https://drive.google.com/file/d/1GezkgqplwTv37NBqxsdcBJ9GH_oLGeZd/preview", "category": "Bleeding"},
    "Bleeding_122315_VID002": {"original": "https://drive.google.com/file/d/1RAi1kXbMJQ1YXitY7q1jx7hXIbgqgJxP/preview", "inpainted": "https://drive.google.com/file/d/1E302xDNL2cT4QvXuIhgeHDGsha-12Txq/preview", "category": "Bleeding"},
    "Dissection_152123_VID005": {"original": "https://drive.google.com/file/d/1yrlMHqvQOUjjPwxDiZWN6ITz-EXFASh_/preview", "inpainted": "https://drive.google.com/file/d/102dq-3qBZGRDAH1Rb5_Lxxk1kKnJ0tW6/preview", "category": "Dissection"},
    "Dissection1_142147_VID002": {"original": "https://drive.google.com/file/d/1wSDTy1Pg_KSXpJEddlQ-uglE0iK76m4P/preview", "inpainted": "https://drive.google.com/file/d/1qJv--2DzcKGNmu1NoFbYnsLgLyrVqRw6/preview", "category": "Dissection"},
    "Landmarking_115418_VID001": {"original": "https://drive.google.com/file/d/1HflnizmwOqj0kHPgn9MPlDldq07rkCT1/preview", "inpainted": "https://drive.google.com/file/d/1ux2CMmHBLIP_eCQAFth4mjyH6ICetbXr/preview", "category": "Landmarking"},
    "Landmarking_115418_VID001_Trim2": {"original": "https://drive.google.com/file/d/14x9xX4m_h8YTN9vxcxWIMfQegYw_SZNr/preview", "inpainted": "https://drive.google.com/file/d/1s4oSoluMhrOxJ8p5fBChsMT1i2ZCGL7U/preview", "category": "Landmarking"},
    "Landmarking_152123_VID002": {"original": "https://drive.google.com/file/d/1IPEkppS00X9popQD2fBm32M5ZF2dVbjv/preview", "inpainted": "https://drive.google.com/file/d/1EILr5f_QzwDEHQTRMeViF0AfifxzXuq1/preview", "category": "Landmarking"},
    "Setup_100813_VID001": {"original": "https://drive.google.com/file/d/1m8ABYyWfbpzd548cM4V6IryWyyCyzCRQ/preview", "inpainted": "https://drive.google.com/file/d/18se2rOGAI4pisdZ_Su-QdjRbu-U35PP1/preview", "category": "Setup"},
    "Setup_115418_VID001": {"original": "https://drive.google.com/file/d/1WHrHbucP2L-eLREzUyYZMeYECvF-D2PR/preview", "inpainted": "https://drive.google.com/file/d/1c5I2_25ol6YKbl6kGsTKqRIU8_pfQc5S/preview", "category": "Setup"},
    "Setup_152123_VID002": {"original": "https://drive.google.com/file/d/1BzinCPGpKjOnedf0wij0_PVjniYyVpV5/preview", "inpainted": "https://drive.google.com/file/d/1yas0kjzvf8AE5FLWyC-6OMG-32L2VRAl/preview", "category": "Setup"},
    "Setup1_162147_VID001": {"original": "https://drive.google.com/file/d/1GIZZYbGGUpPvHKDa_QLronbsHInAuzU9/preview", "inpainted": "https://drive.google.com/file/d/1Duy24DHSueylbHafhE8mC5-kjuc7OryB/preview", "category": "Setup"},
    "Setup1_162147_VID001_Trim2": {"original": "https://drive.google.com/file/d/1SJKziPOqqn6SMgMXgPwngb2DbD2VugAo/preview", "inpainted": "https://drive.google.com/file/d/1RltbU_VnAVOwyxCJOaUmFtISWoVRQ3ce/preview", "category": "Setup"},
    "Suturing_152123_VID008": {"original": "https://drive.google.com/file/d/1cMaoXTaLraBfpJeTSagvV3M4UBLkPDMf/preview", "inpainted": "https://drive.google.com/file/d/14jLmr7KF38jJ-LP7bhzn99T2hb2qfzKc/preview", "category": "Suturing"},
    "Suturing_152123_VID009": {"original": "https://drive.google.com/file/d/1bsjCvPfpk-XQgaCzMz6jANSwTfxpBjgf/preview", "inpainted": "https://drive.google.com/file/d/1aY6EOmJ-VjEtb0aPFE8wvOUbZN7Zhu7z/preview", "category": "Suturing"},
    "Suturing_152123_VID011": {"original": "https://drive.google.com/file/d/18Y28VXrHIkT9cLd6DpZgxITobPSkDFeJ/preview", "inpainted": "https://drive.google.com/file/d/1QA2ddCJXhVftAyavxVWbdEulvBHujhZ8/preview", "category": "Suturing"},
    "Suturing1_110128_VID005": {"original": "https://drive.google.com/file/d/11pP9XOcKLgH0zrhpjXzCwiQHmm8U-Op1/preview", "inpainted": "https://drive.google.com/file/d/1AWcdTb3iWac5GPOMBL7hD_2OWwdaskP0/preview", "category": "Suturing"},
}

CRITERIA = [
    ("specular_severity",    "🔆 Specular Severity",    "Reflections obstructing the field?"),
    ("tissue_visibility",    "🔬 Tissue Visibility",     "Underlying tissue clarity?"),
    ("visual_naturalness",   "🎨 Visual Naturalness",    "Realistic, artifact-free?"),
    ("temporal_consistency", "⏱️ Temporal Consistency", "Smooth, no flickering?"),
    ("clinical_confidence",  "✅ Clinical Confidence",   "Confidence performing procedure?"),
]

def save_to_supabase(row):
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal"}
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/evaluations", headers=hdrs, json=row)
    return r.status_code in [200, 201]

for k, v in {"page":"login","evaluator":{},"assignments":{},"responses":[],"current_video":0}.items():
    if k not in st.session_state: st.session_state[k] = v

def login_page():
    st.markdown('''<div class="header-bar">
        <div><h2 style="margin:0">🏥 Surgical Video Evaluation</h2>
        <p style="margin:2px 0 0;opacity:.85;font-size:.9rem">AI Specular Reflection Removal — Clinical Validation</p></div>
    </div>''', unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.6,1])
    with col:
        st.markdown('''<div style="background:#eff6ff;border-left:4px solid #2563eb;padding:12px;border-radius:6px;margin-bottom:16px;font-size:.95rem">
        You will evaluate <b>17 video pairs</b> — same scene, possibly different processing.<br>
        ⏱️ <b>~20 min</b> &nbsp;|&nbsp; 🔒 Fully blinded &nbsp;|&nbsp; 💾 Auto-saved</div>''', unsafe_allow_html=True)
        with st.form("login", border=True):
            name = st.text_input("Full Name *", placeholder="Dr. John Smith")
            c1, c2 = st.columns(2)
            with c1: specialty = st.selectbox("Specialty", ["Colorectal Surgery","General Surgery","Gastroenterology","Urology","Gynecology","ENT","Other"])
            with c2: experience = st.selectbox("Experience", ["<5 yrs","5–10 yrs","10–20 yrs",">20 yrs"])
            institution = st.text_input("Institution", placeholder="Royal London Hospital")
            if st.form_submit_button("Begin →", type="primary", use_container_width=True):
                if not name.strip(): st.error("Please enter your name.")
                else:
                    st.session_state.evaluator = {"name":name.strip(),"specialty":specialty,"experience":experience,"institution":institution,"timestamp":datetime.now().isoformat()}
                    st.session_state.assignments = {v:{"swap":random.random()>.5} for v in VIDEOS}
                    st.session_state.page = "instructions"; st.rerun()

def instructions_page():
    st.markdown('''<div class="header-bar"><h2 style="margin:0">📋 Instructions</h2></div>''', unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("""
**What to do:**
1. Watch **Video A** and **Video B** (same surgical scene, may differ in processing)
2. Rate each on 5 criteria using sliders (1 = Very Poor → 5 = Excellent)
3. Pick your overall surgical preference

> 🔁 Replay anytime &nbsp;&nbsp; 💾 Auto-saved after each pair &nbsp;&nbsp; 🔒 Blinded study
""")
        if st.button("Start →", type="primary", use_container_width=True):
            st.session_state.page = "evaluate"; st.rerun()

def evaluation_page():
    vids = list(VIDEOS.keys())
    idx = st.session_state.current_video
    if idx >= len(vids): st.session_state.page = "thankyou"; st.rerun(); return

    vn = vids[idx]; vid = VIDEOS[vn]
    swap = st.session_state.assignments[vn]["swap"]
    url_a = vid["inpainted"] if swap else vid["original"]
    url_b = vid["original"] if swap else vid["inpainted"]

    pct = idx / len(vids)
    st.markdown(f'''<div class="header-bar">
        <span>Pair <b>{idx+1}</b> / {len(vids)} &nbsp;·&nbsp;
        <span style="background:rgba(255,255,255,.2);padding:2px 10px;border-radius:20px">{vid["category"]}</span></span>
        <span style="font-size:.9rem;opacity:.85">{int(pct*100)}% complete</span>
    </div>''', unsafe_allow_html=True)
    st.progress(pct)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="vid-label lbl-a">🎬 Video A</div>', unsafe_allow_html=True)
        st.components.v1.iframe(url_a, height=270)
    with c2:
        st.markdown('<div class="vid-label lbl-b">🎬 Video B</div>', unsafe_allow_html=True)
        st.components.v1.iframe(url_b, height=270)

    with st.form(f"f_{vn}", border=False):
        st.markdown('''<div class="rating-header">
            <span>Criterion</span>
            <span style="color:#1e40af;text-align:center">Video A</span>
            <span style="color:#166534;text-align:center">Video B</span></div>''', unsafe_allow_html=True)

        ratings = {}
        for key, label, desc in CRITERIA:
            cc1, cc2, cc3 = st.columns([2,1,1])
            with cc1: st.markdown(f"**{label}** &nbsp; *{desc}*")
            with cc2: ratings[f"{key}_a"] = st.select_slider("A", [1,2,3,4,5], value=3, key=f"A_{key}_{vn}", label_visibility="collapsed")
            with cc3: ratings[f"{key}_b"] = st.select_slider("B", [1,2,3,4,5], value=3, key=f"B_{key}_{vn}", label_visibility="collapsed")

        st.markdown("---")
        c1, c2 = st.columns([3,1])
        with c1: pref = st.radio("🏆 **Prefer for surgery?**", ["Video A","Video B","No Difference"], horizontal=True, key=f"p_{vn}")
        with c2: comments = st.text_input("💬 Notes", key=f"c_{vn}", placeholder="optional")

        if st.form_submit_button("✅ Submit & Next →", type="primary", use_container_width=True):
            row = {"evaluator_name":st.session_state.evaluator["name"],
                   "specialty":st.session_state.evaluator["specialty"],
                   "experience":st.session_state.evaluator["experience"],
                   "institution":st.session_state.evaluator.get("institution",""),
                   "video_name":vn,"category":vid["category"],
                   "video_a_is":"inpainted" if swap else "original",
                   "preference":pref,"comments":comments,**ratings}
            if save_to_supabase(row):
                st.session_state.responses.append(row)
                st.session_state.current_video += 1; st.rerun()
            else: st.error("Save failed — please retry.")

def thankyou_page():
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown('''<div class="header-bar" style="justify-content:center;text-align:center">
            <div><h1 style="margin:0">🎉 Thank You!</h1>
            <p style="margin:6px 0 0;opacity:.9">Responses saved securely.</p></div>
        </div>''', unsafe_allow_html=True)
        name = st.session_state.evaluator.get("name","")
        st.markdown(f"<div style='text-align:center;padding:20px'><h3>Thank you, <b>{name}</b>!</h3><p>You completed all <b>{len(VIDEOS)}</b> video pairs.<br>Your expert input helps advance AI-assisted surgery.</p></div>", unsafe_allow_html=True)
        st.balloons()

{"login":login_page,"instructions":instructions_page,"evaluate":evaluation_page,"thankyou":thankyou_page}[st.session_state.page]()
