import streamlit as st
import httpx
from datetime import datetime

st.set_page_config(page_title="Clinical Video Evaluation", layout="wide", page_icon="🏥")

SUPABASE_URL = "https://jkfdxwhusxpfojvsqtlv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprZmR4d2h1c3hwZm9qdnNxdGx2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4ODI4MjMsImV4cCI6MjA4OTQ1ODgyM30.0oUmlIWgCbVjK2Yqne6AnGiEd3LoqIhucmnGTxFJ5-U"
BANNER_URL = "https://raw.githubusercontent.com/MahmoodAIForge/surgical-video-evaluation/main/banner.png"

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f0f4f8; }
.header-bar { background: linear-gradient(90deg,#0f2b46,#1a5276); padding:16px 28px; border-radius:10px;
               color:white; display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; }
.header-bar h2 { margin:0; font-size:1.6rem; letter-spacing:0.3px; }
.header-bar p { margin:3px 0 0; opacity:.8; font-size:.88rem; }
div[data-testid="stForm"] { background:white; padding:18px; border-radius:10px;
                              box-shadow:0 1px 6px rgba(0,0,0,0.07); }
.info-card { background:#ffffff; border:1px solid #e2e8f0; border-radius:10px;
              padding:18px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.step-num { display:inline-block; background:#1a5276; color:white; width:26px; height:26px;
             border-radius:50%; text-align:center; line-height:26px; font-weight:700; font-size:0.85rem; margin-right:8px; }
.criteria-row { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;
                 padding:12px 16px; margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)

VIDEOS = {
    "Blood_Sucking_100813_VID005": {"url": "https://drive.google.com/file/d/1-ExFjC9qGQy1jzCQ5tOYdMR9T65VPcJV/preview", "category": "Blood Sucking"},
    "Bleeding_100813_VID005": {"url": "https://drive.google.com/file/d/1-OIirR9YlcwMCstV4HwSwfhTkKwBjwRe/preview", "category": "Bleeding"},
    "Bleeding_122315_VID002": {"url": "https://drive.google.com/file/d/1cZKD-5-bSy3cHaA46wccpM9cTCLWWOIV/preview", "category": "Bleeding"},
    "Dissection_152123_VID005": {"url": "https://drive.google.com/file/d/1XSbK8-1Jtc3Aqr95Iw9gHaY51h0CEdEH/preview", "category": "Dissection"},
    "Dissection_142147_VID002": {"url": "https://drive.google.com/file/d/11Clef-d0eFCGa4ElBhaBkAgh6v8gqt3x/preview", "category": "Dissection"},
    "Landmarking_115418_VID001": {"url": "https://drive.google.com/file/d/11q0OSH3xLcLVrCrjxiPuYV_pH9YIMVQt/preview", "category": "Landmarking"},
    "Landmarking_115418_VID001_Trim2": {"url": "https://drive.google.com/file/d/11erbZA0oLTu-jlTKhCube2d7QmRNLKzn/preview", "category": "Landmarking"},
    "Landmarking_152123_VID002": {"url": "https://drive.google.com/file/d/1sDwVv1uR4Hvf5OO-ILsOalgF9XazfQ-M/preview", "category": "Landmarking"},
    "Setup_100813_VID001": {"url": "https://drive.google.com/file/d/1UWlKOvxYqV8Xk6cico_itnlcbu356ilt/preview", "category": "Setup"},
    "Setup_115418_VID001": {"url": "https://drive.google.com/file/d/1BYOG3NNbQZDulXsN53yxJ41Ut0krDNi-/preview", "category": "Setup"},
    "Setup_152123_VID002": {"url": "https://drive.google.com/file/d/1d0_anHzKLrwg7pNxcpDWRlQsS2854u5x/preview", "category": "Setup"},
    "Setup_162147_VID001": {"url": "https://drive.google.com/file/d/11UAmsKTGBrDmlL-VQ1ydbPfNmARboYwK/preview", "category": "Setup"},
    "Setup_162147_VID001_Trim2": {"url": "https://drive.google.com/file/d/1ZKPQ0k50kEEsxhlYpwriihXXpnf9aJzw/preview", "category": "Setup"},
    "Suturing_152123_VID008": {"url": "https://drive.google.com/file/d/1bssK3bq-15LpXdfROtFmSxOspEqXVfVM/preview", "category": "Suturing"},
    "Suturing_152123_VID009": {"url": "https://drive.google.com/file/d/1Y2BFML9ARStN3VLYvDS2HVvgqS2KAzL5/preview", "category": "Suturing"},
    "Suturing_152123_VID011": {"url": "https://drive.google.com/file/d/1RfQTstg86MXknap45EYQm7LvzxwV-Dfe/preview", "category": "Suturing"},
    "Suturing_110128_VID005": {"url": "https://drive.google.com/file/d/1b3YwJN1BafugBTTODxBr3DBzx9e32ujg/preview", "category": "Suturing"},
}

CRITERIA = [
    ("reflection_removal",   "🔆 Reflection Removal",     "How effectively were specular reflections removed?"),
    ("anatomical_clarity",   "🔬 Anatomical Clarity",      "Can you clearly identify the underlying anatomy after cleaning?"),
    ("inpainting_quality",   "🩹 Inpainting Quality",      "Are cleaned areas filled with realistic tissue texture?"),
    ("clinical_confidence",  "✅ Clinical Confidence",      "Would you trust this view for clinical decisions?"),
    ("overall_quality",      "👁️ Overall Visual Quality",  "Rate the overall visual quality of the processed video"),
]

def save_to_supabase(row):
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal"}
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/evaluations", headers=hdrs, json=row)
    return r.status_code in [200, 201]

for k, v in {"page":"login","evaluator":{},"responses":[],"current_video":0}.items():
    if k not in st.session_state: st.session_state[k] = v

def login_page():
    st.markdown("""<div class="header-bar">
        <div><h2>🏥 Specular Reflection Removal</h2>
        <p>Clinical Evaluation of Endoscopic Video Enhancement</p></div>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1,1.6,1])
    with col:
        st.image(BANNER_URL, use_container_width=True)

        st.markdown("""<div class="info-card">
        <p style="font-size:0.95rem;margin:0">
        Thank you for participating in this clinical evaluation study. You will be presented with
        <b>17 endoscopic surgical videos</b>, each displayed as a side-by-side comparison
        of the <b>original</b> (left) and <b>processed</b> (right) versions. Please rate the 
        <b>processed video</b> on five clinical criteria.
        </p></div>""", unsafe_allow_html=True)

        with st.form("login", border=True):
            st.markdown("##### Evaluator Information")
            name = st.text_input("Full Name *", placeholder="e.g. Dr. Jane Smith")
            c1, c2 = st.columns(2)
            with c1:
                specialty = st.selectbox("Specialty *", [
                    "Colorectal Surgery","General Surgery","Gastroenterology",
                    "Urology","Gynecology","ENT","Other"])
            with c2:
                experience = st.text_input("Years of Surgical Experience *", placeholder="e.g. 12")
            institution = st.text_input("Institution / Hospital *", placeholder="e.g. University Hospital")

            if st.form_submit_button("Proceed to Evaluation →", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("Please provide your full name.")
                elif not experience.strip():
                    st.error("Please indicate your years of experience.")
                else:
                    st.session_state.evaluator = {
                        "name": name.strip(), "specialty": specialty,
                        "experience": experience.strip(), "institution": institution.strip(),
                        "timestamp": datetime.now().isoformat()}
                    st.session_state.page = "instructions"
                    st.rerun()

def instructions_page():
    st.markdown("""<div class="header-bar">
        <div><h2>📋 Evaluation Protocol</h2>
        <p>Please review the following instructions before proceeding</p></div>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1,2,1])
    with col:
        st.image(BANNER_URL, use_container_width=True, caption="Example: Original (left) vs Processed (right)")

        st.markdown("""<div class="info-card">
        <h4 style="margin-top:0">Procedure</h4>
        <p><span class="step-num">1</span> Each video shows the <b>original recording</b> (left) alongside the
        <b>processed version</b> (right) in a single side-by-side view.</p>
        <p><span class="step-num">2</span> Watch the full video, then rate the <b>processed version</b>
        on five clinical criteria using a 1–5 scale.</p>
        <p><span class="step-num">3</span> Indicate your <b>overall preference</b> for clinical use.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="info-card">
        <h4 style="margin-top:0">Rating Scale</h4>

| Score | Interpretation |
|:-----:|:---------------|
| **1** | Very Poor |
| **2** | Poor |
| **3** | Acceptable |
| **4** | Good |
| **5** | Excellent |

</div>""", unsafe_allow_html=True)

        if st.button("Begin Evaluation →", type="primary", use_container_width=True):
            st.session_state.page = "evaluate"
            st.rerun()

def evaluation_page():
    vids = list(VIDEOS.keys())
    idx = st.session_state.current_video
    if idx >= len(vids):
        st.session_state.page = "thankyou"
        st.rerun()
        return

    vn = vids[idx]
    vid = VIDEOS[vn]
    pct = idx / len(vids)

    st.markdown(f"""<div class="header-bar">
        <span style="font-size:1.1rem">
            Video <b>{idx+1}</b> of {len(vids)} &nbsp;&middot;&nbsp;
            <span style="background:rgba(255,255,255,.15);padding:3px 12px;border-radius:20px;font-size:0.9rem">{vid["category"]}</span>
        </span>
        <span style="font-size:.88rem;opacity:.8">{int(pct*100)}% complete</span>
    </div>""", unsafe_allow_html=True)
    st.progress(pct)

    st.markdown("""<div style="display:flex;justify-content:center;margin-bottom:4px">
        <div style="display:flex;gap:0;font-weight:700;font-size:0.95rem">
            <span style="background:#1a5276;color:white;padding:4px 40px;border-radius:6px 0 0 6px">Original</span>
            <span style="background:#27ae60;color:white;padding:4px 40px;border-radius:0 6px 6px 0">Processed</span>
        </div>
    </div>""", unsafe_allow_html=True)
    st.components.v1.iframe(vid["url"], height=380)

    st.markdown("---")

    with st.form(f"f_{vn}", border=False):
        st.markdown("### Rate the Processed Video &nbsp; <span style='font-size:0.85rem;color:#64748b'>(1 = Very Poor → 5 = Excellent)</span>", unsafe_allow_html=True)

        ratings = {}
        for key, label, desc in CRITERIA:
            st.markdown(f"""<div class="criteria-row">
                <b>{label}</b> &nbsp; <span style="color:#64748b;font-size:0.88rem">— {desc}</span>
            </div>""", unsafe_allow_html=True)
            ratings[key] = st.select_slider(
                label, [1,2,3,4,5], value=3, key=f"{key}_{vn}", label_visibility="collapsed")

        st.markdown("---")
        pref = st.radio("🏆 **Which version would you prefer for clinical use?**",
                        ["Original", "Processed", "No Preference"],
                        horizontal=True, key=f"p_{vn}")
        comments = st.text_area("💬 Additional Comments or Observations", key=f"c_{vn}",
                                 placeholder="Any additional details about this video pair...", height=80)

        if st.form_submit_button("Submit & Continue →", type="primary", use_container_width=True):
            row = {
                "evaluator_name": st.session_state.evaluator["name"],
                "specialty": st.session_state.evaluator["specialty"],
                "experience": st.session_state.evaluator["experience"],
                "institution": st.session_state.evaluator.get("institution",""),
                "video_name": vn,
                "category": vid["category"],
                "preference": pref,
                "comments": comments,
                **ratings
            }
            if save_to_supabase(row):
                st.session_state.responses.append(row)
                st.session_state.current_video += 1
                st.rerun()
            else:
                st.error("Submission failed. Please try again.")

def thankyou_page():
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("""<div class="header-bar" style="justify-content:center;text-align:center">
            <div><h2 style="margin:0">🎉 Evaluation Complete</h2></div>
        </div>""", unsafe_allow_html=True)

        name = st.session_state.evaluator.get("name","")
        st.markdown(f"""<div class="info-card" style="text-align:center;padding:30px">
            <h3 style="margin-top:0">Thank you, {name}.</h3>
            <p style="font-size:1.05rem;color:#475569">
            Your responses have been recorded successfully.<br>
            Your expert evaluation is instrumental in advancing endoscopic imaging quality.<br><br>
            If you have any questions about this study, please contact the research team.
            </p>
        </div>""", unsafe_allow_html=True)
        st.balloons()

{"login":login_page,"instructions":instructions_page,"evaluate":evaluation_page,"thankyou":thankyou_page}[st.session_state.page]()
