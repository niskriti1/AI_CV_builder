# main.py
import os
from dotenv import load_dotenv
import streamlit as st
from cvbuilder import build_resume, markdown_to_docx, markdown_to_pdf, TEMPLATE_PREVIEWS

# Load environment variables
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

st.set_page_config(page_title="AI CV Builder", page_icon="📄", layout="wide")

# Custom CSS for better styling
st.markdown(
    """
<style>
.template-preview {
    border: 3px solid #4CAF50;
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    background: white;
    box-shadow: 0 6px 12px rgba(76, 175, 80, 0.2);
    height: 600px;
    overflow-y: auto;
    font-size: 0.9em;
}

.template-preview.selected {
    border-color: #4CAF50;
    background: white;
    box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3);
}

.template-header {
    text-align: center;
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 10px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.modern-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.professional-header {
    background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
}

.creative-header {
    background: linear-gradient(90deg, #ff7e5f 0%, #feb47b 100%);
}

.stTextArea textarea {
    font-family: 'Courier New', monospace;
}

.resume-content {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
}

.download-section {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-top: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("📄 AI Resume Builder")
st.markdown(
    "Create professional resumes with AI assistance - Choose your style, see it live!"
)

# Initialize session state
if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = ""
if "selected_template" not in st.session_state:
    st.session_state.selected_template = "modern"
if "show_input" not in st.session_state:
    st.session_state.show_input = True


# Step 1: Template Selection
if st.session_state.show_input:

    st.sidebar.header("🎨 Step 1: Choose Your Resume Style")

    # Template dropdown selection
    col_dropdown, col_spacer = st.columns([1, 2])

    with col_dropdown:
        template_options = {
            "modern": "🔷 Modern Template",
            "professional": "🔶 Professional Template",
            "creative": "♦️ Creative Template",
        }

        selected_template = st.sidebar.selectbox(
            "Choose a template style:",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x],
            index=list(template_options.keys()).index(
                st.session_state.selected_template
            ),
            key="template_dropdown",
        )

        # Update session state if selection changed
        if selected_template != st.session_state.selected_template:
            st.session_state.selected_template = selected_template

    # Template descriptions
    template_descriptions = {
        "modern": "Clean, minimalist design perfect for tech roles",
        "professional": "Corporate, formal style ideal for business roles",
        "creative": "Engaging, modern design great for creative fields",
    }

    st.info(
        f"**{template_options[st.session_state.selected_template]}**: {template_descriptions[st.session_state.selected_template]}"
    )

    # Show selected template preview
    st.subheader("👀 Template Preview")
    st.markdown(
        TEMPLATE_PREVIEWS[st.session_state.selected_template], unsafe_allow_html=True
    )

    st.markdown("---")

    # Step 2: Input Information
    st.header("📋 Step 2: Enter Your Information")

    col_input1, col_input2 = st.columns([2, 1])

    with col_input1:
        user_input = st.text_area(
            "Enter your resume details:",
            height=400,
            help="Include all relevant information for your resume such as name, contact info, education, skills, work experience, projects, and a brief summary.",
        )

    with col_input2:
        st.markdown("### 💡 Tips for best results:")
        st.info(
            """
        **📝 Include:**
        - Full name and contact info
        - Education details
        - Skills (will be auto-categorized)
        - Work experience with achievements
        - Projects with descriptions
        - Professional summary
        
        **🎯 Pro Tips:**
        - Be specific about technologies used
        - Include quantifiable achievements
        - Mention GitHub links for projects
        - Keep descriptions concise but detailed
        """
        )

    # Generate Button
    st.markdown("---")
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    with col_gen2:
        if st.button(
            "🚀 Generate My Resume",
            type="primary",
            use_container_width=True,
            key="generate_btn",
        ):
            if not user_input.strip():
                st.warning("⚠️ Please enter your resume information first.")
            else:
                with st.spinner(
                    f"🔄 Creating your {st.session_state.selected_template} resume..."
                ):
                    try:
                        st.session_state.generated_resume = build_resume(
                            api_key=api_key,
                            input_text=user_input,
                            template=st.session_state.selected_template,
                        )
                        st.session_state.show_input = False
                        st.success("✅ Resume generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating resume: {str(e)}")

# Step 3: Show Generated Resume
else:
    # Back button
    if st.button("← Back to Edit", key="back_btn"):
        st.session_state.show_input = True
        st.rerun()

    st.header(f"✨ Your {st.session_state.selected_template.title()} Resume")

    # Editable Resume Section
    st.subheader("✏️ Edit Your Resume")

    edited_resume = st.text_area(
        "Make any changes to your resume:",
        value=st.session_state.generated_resume,
        height=300,
        help="Edit the markdown content directly. Changes will be reflected in the preview below.",
    )

    # Update session state if content changed
    if edited_resume != st.session_state.generated_resume:
        st.session_state.generated_resume = edited_resume

    # Live Preview
    st.subheader("👀 Live Preview")
    st.markdown('<div class="resume-content">', unsafe_allow_html=True)
    st.markdown(st.session_state.generated_resume, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Download Section
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.subheader("📥 Download Your Resume")

    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])

    with col_dl1:
        format_choice = st.selectbox("📄 Choose format:", ["PDF", "DOCX"])

    with col_dl2:
        if st.button("📥 Prepare Download", type="primary", use_container_width=True):
            try:
                with st.spinner(f"🔄 Converting to {format_choice}..."):
                    if format_choice == "PDF":
                        resume_file = markdown_to_pdf(st.session_state.generated_resume)
                        mime_type = "application/pdf"
                        file_name = f"resume_{st.session_state.selected_template}.pdf"
                    else:
                        resume_file = markdown_to_docx(
                            st.session_state.generated_resume
                        )
                        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        file_name = f"resume_{st.session_state.selected_template}.docx"

                    st.session_state.download_file = resume_file
                    st.session_state.file_name = file_name
                    st.session_state.mime_type = mime_type
                    st.success(f"✅ {format_choice} ready!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with col_dl3:
        if hasattr(st.session_state, "download_file"):
            st.download_button(
                label=f"💾 Download {st.session_state.file_name.split('.')[-1].upper()}",
                data=st.session_state.download_file,
                file_name=st.session_state.file_name,
                mime=st.session_state.mime_type,
                use_container_width=True,
            )

    # Copy markdown option
    with st.expander("📋 Copy Markdown Code"):
        st.code(st.session_state.generated_resume, language="markdown")
        st.info("💡 You can copy the markdown code above to use elsewhere!")

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; margin-top: 2rem;'>
<p>🤖 Powered by AI | 📝 Built with Streamlit | ✨ Create professional resumes in minutes</p>
</div>
""",
    unsafe_allow_html=True,
)
