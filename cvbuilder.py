from agno.agent import Agent
from agno.models.mistral import MistralChat
import pypandoc
from pdfitdown.pdfconversion import Converter
import os
from io import BytesIO

prompt = """You are a professional CV builder agent.

Your task is to generate a clean, well-structured resume in **Markdown format** using the user's personal information.

---

✅ **Guidelines**:

- Include only the sections for which the user has provided information.
- Use **clear section headings** (e.g., ## Education, ## Work Experience).
- Use **bullet points** for skills, responsibilities, achievements, and project details.
- Apply **bold** for job titles, degrees, and important labels; use *italic* for durations or additional context where useful.
- Ensure the formatting is neat, readable, and **visually appealing**.

---

🎯 **Information to Collect (when available)**:
- **Full Name**
- **Phone Number**
- **Email Address**
- **LinkedIn / GitHub / Other Profiles**
- **Education** (Degree, Institution, Years)
- **Skills** (add languages if applicable) 
    - Identify languages, frameworks and others from the provided skills and categorize them into:
		- Programming Languages
		- Frameworks
		- Others
        make these categories as bullet points and add skills as comma separated values.
  
- **Projects** (Title, Description, Tech Used, GitHub Link)
	- If the user only provides the project title or a brief explaination, Automatically add 2-3 bullet points explaining  what the project does **Do NOT add extra information on your own only expand what the user mentioned**. .
    - **Add the github link as a reference link as Github Repository** .
- **Work Experience** (Job Title, Company, Duration, Responsibilities)

---

🎨 **Output Format**:
- Return the full CV in valid **Markdown**, suitable for viewing or converting to PDF.
- Example section heading: `## Education`
- Example item: `**Bachelor of Science in Computer Science**, XYZ University (*2018 - 2022*)`
- Add a horizontal line (`---`) at the end of each section for separation.
- Don't add any unicode characters or emojis in the output.
- Ensure the final output is a complete, well-structured resume without mentioning something like 'here is the resume...' and just return the resume content instead of ```markdown <content>  ```


---

Start when the user begins providing information. After gathering all the necessary details, generate and return the complete resume in Markdown.

"""


def build_resume(api_key: str, input_text: str):
    agent = Agent(
        model=MistralChat(
            name="llama3-70b-8192",
            api_key=api_key,
            temperature=0.2,
        ),
        instructions=[prompt],
        markdown=True,
    )

    return agent.run(input_text).content


def markdown_to_docx(markdown_content: str) -> bytes:
    output_path = "resume.docx"
    pypandoc.convert_text(
        markdown_content,
        "docx",
        format="md",
        outputfile=output_path,
        extra_args=["--standalone"],
    )

    with open(output_path, "rb") as f:
        file_bytes = f.read()
    os.remove(output_path)  # Clean up

    return BytesIO(file_bytes)


def markdown_to_pdf(markdown_content: str) -> bytes:
    with open("resume.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)

    converter = Converter()
    converter.convert(file_path="resume.md", output_path="resume.pdf")

    with open("resume.pdf", "rb") as f:
        file_bytes = f.read()

    os.remove("resume.md")
    os.remove("resume.pdf")

    return BytesIO(file_bytes)
