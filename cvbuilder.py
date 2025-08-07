# cvbuilder.py
from agno.agent import Agent
from agno.models.mistral import MistralChat
import pypandoc
from pdfitdown.pdfconversion import Converter
import os
from io import BytesIO

# Template definitions
TEMPLATES = {
    "modern": """You are a professional CV builder agent creating a modern, clean resume.
Your task is to generate a well-structured resume in **Markdown format** using the user's personal information.

✅ **Modern Template Guidelines**:
- Use clean, minimalist design with clear section separation
- Include only sections with provided information
- Use **bold** for names, job titles, degrees, and section headers
- Use *italic* for durations, companies, and universities
- Apply bullet points for skills, responsibilities, and achievements
- Add horizontal lines (---) between major sections

🎯 **Structure**:
# [Full Name]
**Email:** [email] | **Phone:** [phone] | **LinkedIn:** [linkedin] | **GitHub:** [github]

---

## Professional Summary
[Brief 2-3 line summary if provided]

---

## Skills
### Programming Languages
[comma-separated list]

### Frameworks & Technologies
[comma-separated list]

### Other Skills
[comma-separated list]

---

## Work Experience
**[Job Title]** | *[Company]* | *[Duration]*
- [Responsibility/Achievement]
- [Responsibility/Achievement]

---

## Projects
**[Project Name]** | [GitHub Repository](link)
- [Project description point 1]
- [Project description point 2]
- **Technologies:** [tech stack]

---

## Education
**[Degree]** | *[University]* | *[Years]*

---

Output only the markdown content without code blocks or explanations.""",
    "professional": """You are a professional CV builder agent creating a formal, corporate-style resume.
Your task is to generate a structured resume in **Markdown format** using the user's personal information.

✅ **Professional Template Guidelines**:
- Use formal, corporate structure
- Emphasize achievements and quantifiable results
- Use **bold** for key information and section headers
- Use bullet points with action verbs
- Include horizontal lines for section separation

🎯 **Structure**:
# [FULL NAME]
**Contact Information**
- **Email:** [email]
- **Phone:** [phone] 
- **LinkedIn:** [linkedin]
- **GitHub:** [github]

---

## OBJECTIVE
[Professional objective if provided]

---

## CORE COMPETENCIES
**Programming Languages:** [list]
**Frameworks & Technologies:** [list]  
**Additional Skills:** [list]

---

## PROFESSIONAL EXPERIENCE
### [Job Title]
**[Company Name]** | *[Duration]*
- [Achievement/Responsibility with action verb]
- [Achievement/Responsibility with action verb]

---

## KEY PROJECTS
### [Project Name]
**Repository:** [GitHub Repository](link)
- [Detailed project description]
- [Key features and technologies]
- **Technical Stack:** [technologies used]

---

## EDUCATION
**[Degree Program]**
*[University Name]* | *[Graduation Year]*

---

Output only the markdown content without code blocks or explanations.""",
    "creative": """You are a professional CV builder agent creating a creative, visually appealing resume.
Your task is to generate an engaging resume in **Markdown format** using the user's personal information.

✅ **Creative Template Guidelines**:
- Use engaging, modern formatting with emojis for sections
- Emphasize creativity and personality
- Use **bold** and *italic* creatively for visual hierarchy
- Include project highlights and personal touches

🎯 **Structure**:
# 🚀 [Full Name]

📧 [email] • 📱 [phone] • 💼 [linkedin] • 💻 [github]

---

## 💡 About Me
[Personal summary if provided]

---

## 🛠️ Technical Arsenal

**💻 Programming Languages**
[comma-separated list]

**🔧 Frameworks & Tools** 
[comma-separated list]

**⚡ Other Skills**
[comma-separated list]

---

## 💼 Experience Journey

### 🎯 [Job Title]
**[Company]** • *[Duration]*
• [Achievement/responsibility]
• [Achievement/responsibility]

---

## 🚀 Featured Projects

### 📦 [Project Name]
*[GitHub Repository](link)*

🔹 [Project feature/description]
🔹 [Project feature/description]  
**🔧 Built with:** [technologies]

---

## 🎓 Education

**[Degree]**
*[University]* • *[Years]*

---

Output only the markdown content without code blocks or explanations.""",
}

# Sample previews for templates
TEMPLATE_PREVIEWS = {
    "modern": """# John Smith
**Email:** john@example.com | **Phone:** +1-234-567-8900 | **LinkedIn:** linkedin.com/in/johnsmith | **GitHub:** github.com/johnsmith

---

## Skills
### Programming Languages
Python, JavaScript, Java

### Frameworks & Technologies
React, Node.js, Django, PostgreSQL

### Other Skills
Git, Docker, AWS, Agile

---

## Work Experience
**Software Developer** | *TechCorp Inc.* | *2024 - Present*
- Developed scalable web applications using React and Node.js
- Collaborated with cross-functional teams to deliver projects on time

---

## Projects
**E-commerce Platform** | [GitHub Repository](https://github.com/johnsmith/ecommerce)
- Built full-stack shopping website with payment integration
- Implemented user authentication and admin dashboard
- **Technologies:** React, Express, MongoDB

---

## Education
**Bachelor of Computer Science** | *MIT* | *2020 - 2024*""",
    "professional": """# JOHN SMITH
**Contact Information**
- **Email:** john@example.com
- **Phone:** +1-234-567-8900
- **LinkedIn:** linkedin.com/in/johnsmith
- **GitHub:** github.com/johnsmith

---

## CORE COMPETENCIES
**Programming Languages:** Python, JavaScript, Java
**Frameworks & Technologies:** React, Node.js, Django, PostgreSQL
**Additional Skills:** Git, Docker, AWS, Project Management

---

## PROFESSIONAL EXPERIENCE
### Software Developer
**TechCorp Inc.** | *2024 - Present*
- Developed and maintained scalable web applications using modern frameworks
- Collaborated with cross-functional teams to deliver high-quality software solutions

---

## KEY PROJECTS
### E-commerce Platform
**Repository:** [GitHub Repository](https://github.com/johnsmith/ecommerce)
- Architected and developed full-stack e-commerce solution with payment processing
- Implemented comprehensive user management and administrative features
- **Technical Stack:** React, Express.js, MongoDB, Stripe API

---

## EDUCATION
**Bachelor of Computer Science**
*Massachusetts Institute of Technology* | *2024*""",
    "creative": """# 🚀 John Smith

📧 john@example.com • 📱 +1-234-567-8900 • 💼 linkedin.com/in/johnsmith • 💻 github.com/johnsmith

---

## 🛠️ Technical Arsenal

**💻 Programming Languages**
Python, JavaScript, Java

**🔧 Frameworks & Tools** 
React, Node.js, Django, PostgreSQL

**⚡ Other Skills**
Git, Docker, AWS, Creative Problem Solving

---

## 💼 Experience Journey

### 🎯 Software Developer
**TechCorp Inc.** • *2024 - Present*
• Crafted beautiful, responsive web applications with cutting-edge technologies
• Transformed complex requirements into elegant, user-friendly solutions

---

## 🚀 Featured Projects

### 📦 E-commerce Platform
*[GitHub Repository](https://github.com/johnsmith/ecommerce)*

🔹 Full-stack shopping experience with seamless payment integration
🔹 Dynamic admin dashboard with real-time analytics
**🔧 Built with:** React, Express, MongoDB, Stripe

---

## 🎓 Education

**Bachelor of Computer Science**
*MIT* • *2024*""",
}


def build_resume(api_key: str, input_text: str, template: str = "modern"):
    prompt = TEMPLATES.get(template, TEMPLATES["modern"])

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
    os.remove(output_path)
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
