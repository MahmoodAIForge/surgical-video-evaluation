import streamlit as st
import random
import json
import os
from datetime import datetime

st.set_page_config(page_title="Surgical Video Evaluation", layout="wide", page_icon="🏥")

VIDEOS = {
    "Blood_Sucking_100813_VID005": {
        "original": "https://drive.google.com/file/d/156hCT5sOOGlVZZ9bHGN-3SaaAIjqQcSP/preview",
        "inpainted": "https://drive.google.com/file/d/1W4K2ynUwbfEuDDsboImOqQKv4j1KUYDM/preview",
        "category": "Blood Sucking"
    },
    "Bleeding_100813_VID005": {
        "original": "https://drive.google.com/file/d/1nhchHUosO-Apkgf7ResMkNOK0BuRyZJ6/preview",
        "inpainted": "https://drive.google.com/file/d/1GezkgqplwTv37NBqxsdcBJ9GH_oLGeZd/preview",
        "category": "Bleeding"
    },
    "Bleeding_122315_VID002": {
        "original": "https://drive.google.com/file/d/1RAi1kXbMJQ1YXitY7q1jx7hXIbgqgJxP/preview",
        "inpainted": "https://drive.google.com/file/d/1E302xDNL2cT4QvXuIhgeHDGsha-12Txq/preview",
        "category": "Bleeding"
    },
    "Dissection_152123_VID005": {
        "original": "https://drive.google.com/file/d/1yrlMHqvQOUjjPwxDiZWN6ITz-EXFASh_/preview",
        "inpainted": "https://drive.google.com/file/d/102dq-3qBZGRDAH1Rb5_Lxxk1kKnJ0tW6/preview",
        "category": "Dissection"
    },
    "Dissection1_142147_VID002": {
        "original": "https://drive.google.com/file/d/1wSDTy1Pg_KSXpJEddlQ-uglE0iK76m4P/preview",
        "inpainted": "https://drive.google.com/file/d/1qJv--2DzcKGNmu1NoFbYnsLgLyrVqRw6/preview",
        "category": "Dissection"
    },
    "Landmarking_115418_VID001": {
        "original": "https://drive.google.com/file/d/1HflnizmwOqj0kHPgn9MPlDldq07rkCT1/preview",
        "inpainted": "https://drive.google.com/file/d/1ux2CMmHBLIP_eCQAFth4mjyH6ICetbXr/preview",
        "category": "Landmarking"
    },
    "Landmarking_115418_VID001_Trim2": {
        "original": "https://drive.google.com/file/d/14x9xX4m_h8YTN9vxcxWIMfQegYw_SZNr/preview",
        "inpainted": "https://drive.google.com/file/d/1s4oSoluMhrOxJ8p5fBChsMT1i2ZCGL7U/preview",
        "category": "Landmarking"
    },
    "Landmarking_152123_VID002": {
        "original": "https://drive.google.com/file/d/1IPEkppS00X9popQD2fBm32M5ZF2dVbjv/preview",
        "inpainted": "https://drive.google.com/file/d/1EILr5f_QzwDEHQTRMeViF0AfifxzXuq1/preview",
        "category": "Landmarking"
    },
    "Setup_100813_VID001": {
        "original": "https://drive.google.com/file/d/1m8ABYyWfbpzd548cM4V6IryWyyCyzCRQ/preview",
        "inpainted": "https://drive.google.com/file/d/18se2rOGAI4pisdZ_Su-QdjRbu-U35PP1/preview",
        "category": "Setup"
    },
    "Setup_115418_VID001": {
        "original": "https://drive.google.com/file/d/1WHrHbucP2L-eLREzUyYZMeYECvF-D2PR/preview",
        "inpainted": "https://drive.google.com/file/d/1c5I2_25ol6YKbl6kGsTKqRIU8_pfQc5S/preview",
        "category": "Setup"
    },
    "Setup_152123_VID002": {
        "original": "https://drive.google.com/file/d/1BzinCPGpKjOnedf0wij0_PVjniYyVpV5/preview",
        "inpainted": "https://drive.google.com/file/d/1yas0kjzvf8AE5FLWyC-6OMG-32L2VRAl/preview",
        "category": "Setup"
    },
    "Setup1_162147_VID001": {
        "original": "https://drive.google.com/file/d/1GIZZYbGGUpPvHKDa_QLronbsHInAuzU9/preview",
        "inpainted": "https://drive.google.com/file/d/1Duy24DHSueylbHafhE8mC5-kjuc7OryB/preview",
        "category": "Setup"
    },
    "Setup1_162147_VID001_Trim2": {
        "original": "https://drive.google.com/file/d/1SJKziPOqqn6SMgMXgPwngb2DbD2VugAo/preview",
        "inpainted": "https://drive.google.com/file/d/1RltbU_VnAVOwyxCJOaUmFtISWoVRQ3ce/preview",
        "category": "Setup"
    },
    "Suturing_152123_VID008": {
        "original": "https://drive.google.com/file/d/1cMaoXTaLraBfpJeTSagvV3M4UBLkPDMf/preview",
        "inpainted": "https://drive.google.com/file/d/14jLmr7KF38jJ-LP7bhzn99T2hb2qfzKc/preview",
        "category": "Suturing"
    },
    "Suturing_152123_VID009": {
        "original": "https://drive.google.com/file/d/1bsjCvPfpk-XQgaCzMz6jANSwTfxpBjgf/preview",
        "inpainted": "https://drive.google.com/file/d/1aY6EOmJ-VjEtb0aPFE8wvOUbZN7Zhu7z/preview",
        "category": "Suturing"
    },
    "Suturing_152123_VID011": {
        "original": "https://drive.google.com/file/d/18Y28VXrHIkT9cLd6DpZgxITobPSkDFeJ/preview",
        "inpainted": "https://drive.google.com/file/d/1QA2ddCJXhVftAyavxVWbdEulvBHujhZ8/preview",
        "category": "Suturing"
    },
    "Suturing1_110128_VID005": {
        "original": "https://drive.google.com/file/d/11pP9XOcKLgH0zrhpjXzCwiQHmm8U-Op1/preview",
        "inpainted": "https://drive.google.com/file/d/1AWcdTb3iWac5GPOMBL7hD_2OWwdaskP0/preview",
        "category": "Suturing"
    },
}

CRITERIA = [
    ("specular_severity", "Specular Reflection Severity", "How much do specular reflections obstruct the surgical field?"),
    ("tissue_visibility", "Tissue Visibility", "How clearly can you see the underlying tissue and anatomy?"),
    ("visual_naturalness", "Visual Naturalness", "Does the video look realistic, free from color artifacts or blurring?"),
    ("temporal_consistency", "Temporal Consistency", "Is the video smooth without flickering or frame-to-frame jumps?"),
    ("clinical_confidence", "Clinical Confidence", "How confident would you feel performing a procedure with this view?"),
]

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

if "page" not in st.session_state: st.session_state.page = "login"
if "evaluator" not in st.session_state: st.session_state.evaluator = {}
if "assignments" not in st.session_state: st.session_state.assignments = {}
if "responses" not in st.session_state: st.session_state.responses = []
if "current_video" not in st.session_state: st.session_state.current_video = 0

def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://img.icons8.com/color/96/hospital.png", width=80)
        st.title("Surgical Video Quality Evaluation")
        st.markdown("""
        <div style='background:#f0f7ff;padding:15px;border-radius:10px;margin-bottom:20px'>
        This study evaluates AI-based specular reflection removal in endoscopic surgical videos.
        You will rate <b>17 video pairs</b>. Each pair shows the same scene — one may have been 
        processed by an AI system. Your expert judgment helps validate this technology.
        </div>
        """, unsafe_allow_html=True)

        with st.form("login"):
            name = st.text_input("Full Name *")
            col_a, col_b = st.columns(2)
            with col_a:
                specialty = st.selectbox("Specialty *", [
                    "Colorectal Surgery","General Surgery","Gastroenterology",
                    "Urology","Gynecology","ENT","Other"])
            with col_b:
                experience = st.selectbox("Years of Experience *", ["<5","5-10","10-20",">20"])
            institution = st.text_input("Institution / Hospital")
            submitted = st.form_submit_button("Start Evaluation →", type="primary", use_container_width=True)
            if submitted and name:
                st.session_state.evaluator = {
                    "name": name, "specialty": specialty,
                    "experience": experience, "institution": institution,
                    "timestamp": datetime.now().isoformat()
                }
                assignments = {v: {"swap": random.random() > 0.5} for v in VIDEOS}
                st.session_state.assignments = assignments
                st.session_state.page = "instructions"
                st.rerun()
            elif submitted:
                st.error("Please enter your name.")

def instructions_page():
    st.title("📋 Study Instructions")
    st.markdown("""
    ### How This Works
    - You will see **17 pairs of surgical videos**, labeled **Video A** and **Video B**
    - Both videos show the **same surgical scene** — one may have been AI-processed
    - Rate each video **independently** on 5 clinical criteria (scale 1–5)
    - Select your **overall preference** at the end of each pair

    ### Rating Scale
    | 1 | 2 | 3 | 4 | 5 |
    |---|---|---|---|---|
    | Very Poor | Poor | Acceptable | Good | Excellent |

    ### Notes
    - Watch each video **fully** before rating
    - You may replay videos as needed
    - Your responses are saved automatically after each pair
    - Estimated time: **20–30 minutes**
    """)
    if st.button("Begin Evaluation →", type="primary"):
        st.session_state.page = "evaluate"
        st.rerun()

def evaluation_page():
    vid_names = list(VIDEOS.keys())
    idx = st.session_state.current_video
    if idx >= len(vid_names):
        st.session_state.page = "thankyou"
        st.rerun()
        return

    vid_name = vid_names[idx]
    vid_info = VIDEOS[vid_name]
    swap = st.session_state.assignments[vid_name]["swap"]
    url_a = vid_info["inpainted"] if swap else vid_info["original"]
    url_b = vid_info["original"] if swap else vid_info["inpainted"]

    # Header
    st.markdown(f"### Video Pair {idx+1} of {len(vid_names)} — *{vid_info['category']}*")
    st.progress((idx) / len(vid_names))
    st.markdown("---")

    # Videos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎬 Video A")
        st.components.v1.iframe(url_a, height=300)
    with col2:
        st.markdown("#### 🎬 Video B")
        st.components.v1.iframe(url_b, height=300)

    st.markdown("---")

    with st.form(f"form_{vid_name}"):
        st.markdown("### Rate Each Video (1 = Very Poor, 5 = Excellent)")
        ratings = {}
        for key, label, desc in CRITERIA:
            st.markdown(f"**{label}** — *{desc}*")
            c1, c2 = st.columns(2)
            with c1:
                ratings[f"{key}_A"] = st.select_slider(f"Video A — {label}", [1,2,3,4,5], value=3, key=f"{key}_A_{vid_name}")
            with c2:
                ratings[f"{key}_B"] = st.select_slider(f"Video B — {label}", [1,2,3,4,5], value=3, key=f"{key}_B_{vid_name}")

        st.markdown("---")
        st.markdown("### Overall Preference")
        preference = st.radio(
            "Which video would you prefer during surgery?",
            ["Video A", "Video B", "No Difference"],
            horizontal=True, key=f"pref_{vid_name}"
        )
        comments = st.text_area("Additional comments (optional)", key=f"comments_{vid_name}")
        submitted = st.form_submit_button("Submit & Next →", type="primary", use_container_width=True)

        if submitted:
            response = {
                "video": vid_name, "category": vid_info["category"],
                "swap": swap, "ratings": ratings,
                "preference": preference, "comments": comments,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.responses.append(response)
            st.session_state.current_video += 1
            save_path = os.path.join(RESULTS_DIR,
                f"{st.session_state.evaluator['name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(save_path, "w") as f:
                json.dump({"evaluator": st.session_state.evaluator, "responses": st.session_state.responses}, f, indent=2)
            st.rerun()

def thankyou_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🎉 Thank You!")
        st.markdown(f"""
        ### Thank you, **{st.session_state.evaluator.get('name','')}**!

        You have completed the evaluation of all **{len(VIDEOS)}** video pairs.

        Your expert feedback is invaluable for advancing AI-assisted surgical visualization.

        Your responses have been saved securely.
        """)
        st.balloons()

pages = {"login": login_page, "instructions": instructions_page, "evaluate": evaluation_page, "thankyou": thankyou_page}
pages[st.session_state.page]()
