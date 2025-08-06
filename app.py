import os
from dotenv import load_dotenv
import streamlit as st
from cvbuilder import build_resume, markdown_to_docx, markdown_to_pdf

# Load environment variables from .env file
load_dotenv()

# Get the api key from environment variables
api_key = os.getenv("MISTRAL_API_KEY")

st.set_page_config(page_title="AI CV Builder", page_icon=":briefcase:", layout="wide")


st.title("📄 Resume Builder")

# Input
user_input = st.text_area(
    "📝 Enter your resume data (e.g., JSON, plain text):", height=300
)

# Format selection
format_choice = st.selectbox("📦 Choose format to download resume", ["PDF", "DOCX"])

# Build Button
if st.button("🚀 Build Resume"):
    if not user_input.strip():
        st.warning("Please enter some data first.")
    else:
        # Step 1: Generate markdown
        md_resume = build_resume(api_key=api_key, input_text=user_input)

        st.markdown("### 👁️ Resume Preview (Markdown)")
        st.markdown(md_resume, unsafe_allow_html=True)

        # Step 2: Convert
        if format_choice == "PDF":
            resume_file = markdown_to_pdf(md_resume)
            mime_type = "application/pdf"
            file_name = "resume.pdf"
        else:
            resume_file = markdown_to_docx(md_resume)
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            file_name = "resume.docx"

        # Step 3: Download button
        st.success(f"{format_choice} Resume Generated Successfully!")
        st.download_button(
            label=f"📥 Download {file_name}",
            data=resume_file,
            file_name=file_name,
            mime=mime_type,
        )
