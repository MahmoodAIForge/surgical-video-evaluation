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
.nav-pill { display:inline-block; padding:4px 10px; border-radius:12px; font-size:0.75rem; margin:1px; cursor:pointer; }
.pill-done { background:#dcfce7; color:#166534; }
.pill-current { background:#2563eb; color:white; }
.pill-pending { background:#e2e8f0; color:#64748b; }
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

QUESTIONS = [
    ("reflections_removed",  "Are specular reflections adequately removed?"),
    ("details_preserved",    "Are anatomical details and instrument edges preserved in the processed regions?"),
    ("clinical_trust",       "Would you trust this processed video for clinical use?"),
]

HDRS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json", "Prefer": "return=minimal"}

def save_to_supabase(row):
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/evaluations", headers=HDRS, json=row)
    if r.status_code not in [200, 201]:
        return False, f"{r.status_code} — {r.text}"
    return True, ""

def update_in_supabase(row_id, row):
    hdrs = {**HDRS, "Prefer": "return=representation"}
    r = httpx.patch(f"{SUPABASE_URL}/rest/v1/evaluations?id=eq.{row_id}", headers=hdrs, json=row)
    if r.status_code not in [200, 204]:
        return False, f"{r.status_code} — {r.text}"
    return True, ""

def fetch_submissions(email):
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/evaluations?email=eq.{email}&select=*",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    if r.status_code == 200:
        return {s["video_name"]: s for s in r.json()}
    return {}

for k, v in {"page":"login","evaluator":{},"current_video":0,"submissions":{}}.items():
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
        <b>endoscopic surgical videos</b>, each displayed as a side-by-side comparison
        of the <b>original</b> (left) and <b>processed</b> (right) versions. Please rate the
        <b>processed video</b> on the clinical criteria provided.<br><br>
        💾 Your progress is <b>saved automatically</b> — you can close the browser and resume later by logging in with the same credentials.
        </p></div>""", unsafe_allow_html=True)

        st.markdown("""<div class="info-card">
        <h4 style="margin-top:0">Procedure</h4>
        <p><span class="step-num">1</span> Each video shows the <b>original recording</b> (left) alongside the
        <b>processed version</b> (right) in a single side-by-side view.</p>
        <p><span class="step-num">2</span> Watch the full video, then rate the <b>processed version</b> on the clinical criteria provided.</p>
        </div>""", unsafe_allow_html=True)

        with st.form("login", border=True):
            st.markdown("##### Evaluator Information")
            name = st.text_input("Full Name *", placeholder="e.g. Dr. Jane Smith")
            email = st.text_input("Email *", placeholder="e.g. jane.smith@hospital.org")
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
                elif not email.strip() or "@" not in email:
                    st.error("Please provide a valid email address.")
                elif not experience.strip():
                    st.error("Please indicate your years of experience.")
                else:
                    st.session_state.evaluator = {
                        "name": name.strip(), "email": email.strip().lower(), "specialty": specialty,
                        "experience": experience.strip(), "institution": institution.strip(),
                        "timestamp": datetime.now().isoformat()}
                    # Fetch existing submissions
                    st.session_state.submissions = fetch_submissions(email.strip().lower())
                    n_done = len(st.session_state.submissions)
                    if n_done > 0:
                        st.session_state.page = "evaluate"
                        # Jump to first incomplete video
                        vids = list(VIDEOS.keys())
                        for i, v in enumerate(vids):
                            if v not in st.session_state.submissions:
                                st.session_state.current_video = i
                                break
                        else:
                            st.session_state.current_video = 0
                    else:
                        st.session_state.page = "evaluate"
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
        <p><span class="step-num">2</span> Watch the full video, then rate the <b>processed version</b> on the clinical criteria provided.</p>
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
    vn = vids[idx]
    vid = VIDEOS[vn]
    subs = st.session_state.submissions
    n_done = len(subs)
    existing = subs.get(vn, {})

    # Header
    pct = n_done / len(vids)
    

    rated_tag = " ✅ rated" if vn in subs else ""
    st.markdown(f"""<div class="header-bar">
        <span style="font-size:1.1rem">Video <b>{idx+1}</b> of {len(vids)} · {vid["category"]}{rated_tag}</span>
        <span style="font-size:.88rem;opacity:.8">{n_done}/{len(vids)} rated</span>
    </div>""", unsafe_allow_html=True)

    # Progress pills as clickable buttons
    pill_cols = st.columns(len(vids))
    for i, v in enumerate(vids):
        with pill_cols[i]:
            if v in subs:
                label = f"✅{i+1}"
            elif i == idx:
                label = f"🔵{i+1}"
            else:
                label = f"{i+1}"
            if st.button(label, key=f"pill_{i}", use_container_width=True):
                st.session_state.current_video = i
                st.rerun()

    # Navigation
    c1, c2, c3, c4, c5 = st.columns([1,1,2,1,0.7])
    with c1:
        if st.button("← Previous", disabled=(idx==0), use_container_width=True):
            st.session_state.current_video = idx - 1
            st.rerun()
    with c2:
        if st.button("Next →", disabled=(idx==len(vids)-1), use_container_width=True):
            st.session_state.current_video = idx + 1
            st.rerun()
    with c3:
        jump = st.selectbox("Jump to video", range(1, len(vids)+1), index=idx,
                             format_func=lambda x: f"{'✅' if vids[x-1] in subs else '⭕'} {x}. {VIDEOS[vids[x-1]]['category']}",
                             label_visibility="collapsed")
        if jump - 1 != idx:
            st.session_state.current_video = jump - 1
            st.rerun()
    with c4:
        if n_done == len(vids):
            if st.button("🎉 Finish", type="primary", use_container_width=True):
                st.session_state.page = "thankyou"
                st.rerun()
    with c5:
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # Video
    st.markdown("""<div style="display:flex;justify-content:center;margin-bottom:4px">
        <div style="display:flex;gap:0;font-weight:700;font-size:0.95rem">
            <span style="background:#1a5276;color:white;padding:4px 40px;border-radius:6px 0 0 6px">Original</span>
            <span style="background:#27ae60;color:white;padding:4px 40px;border-radius:0 6px 6px 0">Processed</span>
        </div>
    </div>""", unsafe_allow_html=True)
    st.components.v1.iframe(vid["url"], height=380)

    # Form
    with st.form(f"f_{vn}", border=False):
        st.markdown("##### Despecularization Quality Assessment")

        ratings = {}
        for key, question in QUESTIONS:
            default_val = existing.get(key, "Yes")
            ratings[key] = st.radio(f"**{question}**", ["Yes", "No"], 
                index=0 if default_val == "Yes" else 1,
                horizontal=True, key=f"{key}_{vn}")

        st.markdown("---")
        default_comments = existing.get("comments", "")
        comments = st.text_area("**Any observations on artifacts, loss of detail, or other issues?**", 
                                 value=default_comments, key=f"c_{vn}", 
                                 placeholder="e.g. colour distortion, blurring, flickering, missing details...", height=100)

        btn_label = "Update Rating →" if vn in subs else "Submit & Continue →"
        if st.form_submit_button(btn_label, type="primary", use_container_width=True):
            row = {
                "evaluator_name": st.session_state.evaluator["name"],
                "email": st.session_state.evaluator["email"],
                "specialty": st.session_state.evaluator["specialty"],
                "experience": st.session_state.evaluator["experience"],
                "institution": st.session_state.evaluator.get("institution",""),
                "video_name": vn,
                "category": vid["category"],
                "comments": comments,
                **ratings
            }
            if vn in subs:
                ok, err = update_in_supabase(subs[vn]["id"], row)
            else:
                ok, err = save_to_supabase(row)

            if ok:
                st.session_state.submissions = fetch_submissions(st.session_state.evaluator["name"])
                # Auto-advance to next unrated
                if vn not in subs:
                    for i in range(idx+1, len(vids)):
                        if vids[i] not in st.session_state.submissions:
                            st.session_state.current_video = i
                            break
                    else:
                        if len(st.session_state.submissions) == len(vids):
                            st.session_state.page = "thankyou"
                st.rerun()
            else:
                st.error(f"Debug: {err}")

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
            You have rated all <b>{len(VIDEOS)}</b> videos.<br>
            Your responses have been recorded successfully.<br><br>
            You can return anytime to update your ratings by logging in with the same credentials.
            </p>
        </div>""", unsafe_allow_html=True)
        if st.button("← Back to Videos", use_container_width=True):
            st.session_state.page = "evaluate"
            st.session_state.current_video = 0
            st.rerun()
        st.balloons()

{"login":login_page,"instructions":instructions_page,"evaluate":evaluation_page,"thankyou":thankyou_page}[st.session_state.page]()
