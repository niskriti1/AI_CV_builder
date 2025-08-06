# AI CV Builder System

## Overview

An AI-powered CV builder system that leverages an intelligent agent to automatically generate a professional resume based on user-provided details.

The application:

- Accepts user input data (e.g., personal info, education, experience).
- Uses an AI agent to generate a resume in Markdown format.
- Displays the resume as Markdown preview.
- Allows downloading the resume as PDF or DOCX file.

## Features

- **AI-powered Resume Generation:** Automatically create a structured resume using an agent based on raw user input.
- **Multi-format Export:** Download the final resume in PDF or DOCX format.
- **User-friendly Interface:** Simple input form and interactive markdown preview for easy customization.

## How It Works

1. User enters their details in a text input.
2. The AI agent processes the input and returns a formatted resume in Markdown.
3. The Markdown preview is displayed.
4. User selects an output format (PDF or DOCX).
5. The resume is converted and offered as a downloadable file.

## Technologies Used

- Python
- Streamlit for the web app interface
- AI agent (e.g., MistralAI LLM)
- Markdown for resume formatting
- PDF/DOCX conversion libraries (pypandoc, pdfitdown)

## ⚙️ Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/niskriti1/AI_CV_builder.git
```

# 2. (Optional) Create a virtual environment

```
python -m venv venv
source venv/bin/activate
```

# 3. Install dependencies

```
pip install -r requirements.txt
```

# 4. Run the app

```
streamlit run app.py
```
