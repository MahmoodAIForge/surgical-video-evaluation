import streamlit as st
import random
import httpx
import json
from datetime import datetime

st.set_page_config(page_title="Surgical Video Evaluation", layout="wide", page_icon="🏥")

SUPABASE_URL = "https://jkfdxwhusxpfojvsqtlv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprZmR4d2h1c3hwZm9qdnNxdGx2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4ODI4MjMsImV4cCI6MjA4OTQ1ODgyM30.0oUmlIWgCbVjK2Yqne6AnGiEd3LoqIhucmnGTxFJ5-U"

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    .video-label { font-size: 1.3rem; font-weight: 700; color: #1e3a5f; text-align: center; padding: 8px; 
                    background: #e8f0fe; border-radius: 8px; margin-bottom: 8px; }
    .criteria-box { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; 
                     padding: 15px; margin-bottom: 10px; }
    .progress-text { font-size: 0.9rem; color: #64748b; text-align: right; }
    .header-box { background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); 
                   padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px; }
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
    ("specular_severity",   "🔆 Specular Reflection Severity",  "How much do specular reflections obstruct the surgical field?"),
    ("tissue_visibility",   "🔬 Tissue Visibility",              "How clearly can you see the underlying tissue and anatomy?"),
    ("visual_naturalness",  "🎨 Visual Naturalness",             "Does the video look realistic, free from color artifacts or blurring?"),
    ("temporal_consistency","⏱️ Temporal Consistency",           "Is the video smooth without flickering or frame-to-frame jumps?"),
    ("clinical_confidence", "✅ Clinical Confidence",            "How confident would you feel performing a procedure with this view?"),
]

def save_to_supabase(row):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json", "Prefer": "return=minimal"}
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/evaluations", headers=headers, json=row)
    return r.status_code in [200, 201]

# Session state
for k, v in {"page":"login","evaluator":{},"assignments":{},"responses":[],"current_video":0}.items():
    if k not in st.session_state: st.session_state[k] = v

# ── LOGIN ────────────────────────────────────────────────────
def login_page():
    st.markdown("""
    <div class="header-box">
        <h1 style="margin:0;font-size:2rem;">🏥 Surgical Video Quality Evaluation</h1>
        <p style="margin:8px 0 0 0;opacity:0.9;">AI-Based Specular Reflection Removal — Clinical Validation Study</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='background:#eff6ff;padding:16px;border-left:4px solid #2563eb;border-radius:6px;margin-bottom:20px'>
        <b>About this study:</b> You will evaluate <b>17 pairs</b> of endoscopic surgical videos. 
        Each pair shows the same surgical scene — one video may have been processed by an AI 
        specular reflection removal system. Your expert judgment helps validate this technology.
        <br><br>⏱️ Estimated time: <b>20–30 minutes</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login", border=True):
            st.markdown("#### 👤 Your Details")
            name = st.text_input("Full Name *", placeholder="e.g. Dr. John Smith")
            c1, c2 = st.columns(2)
            with c1:
                specialty = st.selectbox("Specialty *", ["Colorectal Surgery","General Surgery",
                    "Gastroenterology","Urology","Gynecology","ENT","Other"])
            with c2:
                experience = st.selectbox("Years of Experience *", ["<5","5–10","10–20",">20"])
            institution = st.text_input("Institution / Hospital", placeholder="e.g. Royal London Hospital")

            submitted = st.form_submit_button("Begin Evaluation →", type="primary", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Please enter your name.")
                else:
                    st.session_state.evaluator = {"name": name.strip(), "specialty": specialty,
                        "experience": experience, "institution": institution,
                        "timestamp": datetime.now().isoformat()}
                    st.session_state.assignments = {v: {"swap": random.random()>0.5} for v in VIDEOS}
                    st.session_state.page = "instructions"
                    st.rerun()

# ── INSTRUCTIONS ─────────────────────────────────────────────
def instructions_page():
    st.markdown("""
    <div class="header-box">
        <h1 style="margin:0;font-size:1.8rem;">📋 Study Instructions</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        ### How This Works
        1. You will see **17 pairs** of surgical videos labeled **Video A** and **Video B**
        2. Both show the **same surgical scene** — one may be AI-processed
        3. Rate each video **independently** on 5 clinical criteria
        4. Select your **overall preference** at the end of each pair

        ### Rating Scale
        | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
        |---|---|---|---|---|
        | Very Poor | Poor | Acceptable | Good | Excellent |

        ### Important
        - ▶️ Watch **both videos fully** before rating
        - 🔁 You may **replay** videos as many times as needed
        - 💾 Responses are **saved automatically** after each pair
        - 🔒 This is a **blinded** study — video labels (A/B) are randomised
        """)

        if st.button("Start Evaluation →", type="primary", use_container_width=True):
            st.session_state.page = "evaluate"
            st.rerun()

# ── EVALUATION ───────────────────────────────────────────────
def evaluation_page():
    vid_names = list(VIDEOS.keys())
    idx = st.session_state.current_video
    if idx >= len(vid_names):
        st.session_state.page = "thankyou"
        st.rerun()
        return

    vid_name = vid_names[idx]
    vid = VIDEOS[vid_name]
    swap = st.session_state.assignments[vid_name]["swap"]
    url_a = vid["inpainted"] if swap else vid["original"]
    url_b = vid["original"] if swap else vid["inpainted"]

    # Progress
    pct = idx / len(vid_names)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
        <span style="font-weight:700;font-size:1.1rem;color:#1e3a5f">
            Video Pair {idx+1} of {len(vid_names)} &nbsp;·&nbsp; 
            <span style="background:#dbeafe;padding:3px 10px;border-radius:20px;font-size:0.9rem">{vid['category']}</span>
        </span>
        <span class="progress-text">{int(pct*100)}% complete</span>
    </div>
    """, unsafe_allow_html=True)
    st.progress(pct)
    st.markdown("---")

    # Videos side by side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="video-label">🎬 Video A</div>', unsafe_allow_html=True)
        st.components.v1.iframe(url_a, height=320)
    with col2:
        st.markdown('<div class="video-label">🎬 Video B</div>', unsafe_allow_html=True)
        st.components.v1.iframe(url_b, height=320)

    st.markdown("---")

    with st.form(f"form_{vid_name}", border=False):
        st.markdown("### 📊 Rate Each Video &nbsp; <span style='font-size:0.85rem;color:#64748b'>(1 = Very Poor → 5 = Excellent)</span>", 
                    unsafe_allow_html=True)

        ratings = {}
        for key, label, desc in CRITERIA:
            with st.container():
                st.markdown(f"""
                <div class="criteria-box">
                <b>{label}</b><br>
                <span style="color:#64748b;font-size:0.9rem">{desc}</span>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    ratings[f"{key}_a"] = st.select_slider(
                        "Video A", [1,2,3,4,5], value=3, key=f"{key}_A_{vid_name}")
                with c2:
                    ratings[f"{key}_b"] = st.select_slider(
                        "Video B", [1,2,3,4,5], value=3, key=f"{key}_B_{vid_name}")

        st.markdown("---")
        st.markdown("### 🏆 Overall Preference")
        preference = st.radio(
            "Which video would you prefer during surgery?",
            ["Video A", "Video B", "No Difference"],
            horizontal=True, key=f"pref_{vid_name}"
        )
        comments = st.text_area("💬 Additional comments (optional)", 
                                 placeholder="Any observations about this video pair...",
                                 key=f"comments_{vid_name}")

        submitted = st.form_submit_button("✅ Submit & Next →", type="primary", use_container_width=True)
        if submitted:
            row = {
                "evaluator_name": st.session_state.evaluator["name"],
                "specialty": st.session_state.evaluator["specialty"],
                "experience": st.session_state.evaluator["experience"],
                "institution": st.session_state.evaluator.get("institution",""),
                "video_name": vid_name,
                "category": vid["category"],
                "video_a_is": "inpainted" if swap else "original",
                "preference": preference,
                "comments": comments,
                **ratings
            }
            ok = save_to_supabase(row)
            if ok:
                st.session_state.responses.append(row)
                st.session_state.current_video += 1
                st.rerun()
            else:
                st.error("Failed to save. Please try again.")

# ── THANK YOU ────────────────────────────────────────────────
def thankyou_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div class="header-box" style="text-align:center">
            <h1 style="margin:0;font-size:2.5rem;">🎉 Thank You!</h1>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style='text-align:center;padding:30px'>
            <h3>Thank you, <b>{st.session_state.evaluator.get('name','')}</b>!</h3>
            <p style='font-size:1.1rem'>You have successfully completed the evaluation of all 
            <b>{len(VIDEOS)} video pairs</b>.</p>
            <p style='color:#64748b'>Your expert feedback is invaluable for advancing 
            AI-assisted surgical visualization.<br>Your responses have been securely saved.</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

# ── ROUTER ───────────────────────────────────────────────────
{"login": login_page, "instructions": instructions_page, 
  "evaluate": evaluation_page, "thankyou": thankyou_page}[st.session_state.page]()
