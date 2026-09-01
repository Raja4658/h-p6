import streamlit as st
import requests

st.set_page_config(page_title="AI Grader Dashboard", layout="wide")

st.title("👨‍🏫 Instructor Review Dashboard")
st.markdown("Evaluate student answers using the Vira Tech AI Auto Grader.")

API_URL = "https://h-p6.vercel.app/api/v1/evaluate"

# Layout
col1, col2 = st.columns(2)

with col1:
    st.header("📝 Submit Assignment")
    
    sub_id = st.text_input("Submission ID", value="student_001")
    q_text = st.text_area("Question Text", value="What is Supervised Learning? Explain with an example.", height=68)
    r_text = st.text_area("Rubric (Criteria)", value="Total marks: 10. Needs definition, mentioning labeled data, and one valid example.", height=68)
    ans_text = st.text_area("Student's Answer", value="Supervised learning is a machine learning method where models are trained using labeled data. For example, predicting house prices.", height=68)
    
    submit = st.button("Evaluate Answer", type="primary")

with col2:
    st.header("📊 Evaluation Results")
    
    if submit:
        with st.spinner("Evaluating response..."):
            # build the data payload
            payload = {
                "submission_id": sub_id,
                "question_id": "q1",
                "rubric_id": "r1",
                "question_text": q_text,
                "answer_text": ans_text,
                "rubric_text": r_text
            }
            
            try:
                res = requests.post(API_URL, json=payload, timeout=30)
                
                if res.status_code == 200:
                    data = res.json()
                    st.success("Done!")
                    
                    # split into metrics
                    m1, m2 = st.columns(2)
                    
                    # safely grab scores just in case the api is acting weird
                    scr = float(data.get('score', 0))
                    mx_scr = float(data.get('max_score', 10))
                    
                    m1.metric("Score Awarded", f"{scr} / {mx_scr}")
                    
                    # check for copy-pasting
                    dup = data.get('duplicate_flag', False)
                    m2.metric("Is Copied?", "⚠️ YES" if dup else "✅ NO")
                    
                    st.subheader("💡 AI Feedback")
                    st.info(data.get('feedback', 'No feedback provided by AI.'))
                    
                    st.subheader("⚙️ Instructor Override")
                    
                    # making sure the slider doesn't break if score > max
                    safe_val = min(scr, mx_scr)
                    new_score = st.number_input("Manual Score Override", min_value=0.0, max_value=mx_scr, value=safe_val)
                    
                    if st.button("Save Score"):
                        st.success(f"Score updated to {new_score}")
                else:
                    st.error(f"Failed to get a valid response. Status: {res.status_code}")
                    
            except requests.exceptions.RequestException as req_err:
                st.error("Looks like the backend API is down. Is uvicorn running?")
            except Exception as e:
                st.error(f"Something went wrong on the dashboard: {str(e)}")
    else:
        st.info("Fill out the details and click Evaluate Answer.")
