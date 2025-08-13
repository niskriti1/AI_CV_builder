# cvbuilder.py
from agno.agent import Agent
from agno.models.mistral import MistralChat
import pypandoc
from pdfitdown.pdfconversion import Converter
import os
from io import BytesIO

# Base instructions shared across all templates
BASE_INSTRUCTIONS = """You are a professional CV builder agent creating a resume.
Your task is to generate a well-structured resume in **Markdown format** using ONLY the user's provided personal information.

✅ **Core Guidelines**:
- Include only sections with provided information - skip any section if no data is available
- Use **bold** for names, job titles, degrees, and section headers
- Use *italic* for durations, companies, and universities
- Apply bullet points for skills, responsibilities, and achievements
- Only include GitHub repository links if explicitly provided by the user
- Don't add any additional information, placeholder links, or fake data
- Return only the resume content without code blocks, explanations, or prefacing text
- Add proper spacing between sections for readability"""

# Template-specific structures
TEMPLATES = {
    "modern": BASE_INSTRUCTIONS
    + """

🎯 **Modern Template Structure**:
- Clean, minimalist design with clear section separation
- Horizontal lines (---) between major sections

# [Full Name]
**Email:** [email] | **Phone:** [phone] | **LinkedIn:** [linkedin] | **GitHub:** [github]

---

## Professional Summary
[Brief 2-3 line summary if provided] \n

---

## Skills
### Programming Languages
[comma-separated list] \n

### Frameworks & Technologies
[comma-separated list] \n

### Other Skills
[comma-separated list] \n

---

## Work Experience
**[Job Title]** | *[Company]* | *[Duration]* \n
- [Responsibility/Achievement] \n
- [Responsibility/Achievement] \n

---

## Projects
**[Project Name]** [Only include repository link if provided: | [GitHub Repository](link)]
- [Project description point 1] \n
- [Project description point 2] \n
- **Technologies:** [tech stack] \n

---

## Education
**[Degree]** | *[University]* | *[Years]*

---""",
    "professional": BASE_INSTRUCTIONS
    + """

🎯 **Professional Template Structure**:
- Formal, corporate structure emphasizing achievements
- Quantifiable results and action verbs preferred

# [FULL NAME]
**Contact Information**
- **Email:** [email] \n
- **Phone:** [phone] \n
- **LinkedIn:** [linkedin] \n
- **GitHub:** [github] \n

---

## OBJECTIVE
[Professional objective if provided] \n

---

## CORE COMPETENCIES
**Programming Languages:** [list] \n
**Frameworks & Technologies:** [list] \n
**Additional Skills:** [list] \n

---

## PROFESSIONAL EXPERIENCE
### [Job Title]
**[Company Name]** | *[Duration]* \n
- [Achievement/Responsibility with action verb] \n
- [Achievement/Responsibility with action verb] \n

---

## KEY PROJECTS
### [Project Name]
[Only include if repository provided: **Repository:** [GitHub Repository](link)]
- [Detailed project description] \n
- [Key features and technologies] \n
- **Technical Stack:** [technologies used] \n

---

## EDUCATION
**[Degree Program]** \n
*[University Name]* | *[Graduation Year]* \n

---""",
    "creative": BASE_INSTRUCTIONS
    + """

🎯 **Creative Template Structure**:
- Engaging, modern formatting with emojis for visual appeal
- Emphasize creativity and personality

# 🚀 [Full Name]

📧 [email] • 📱 [phone] • 💼 [linkedin] • 💻 [github]

---

## 💡 About Me
[Personal summary if provided] \n

---

## 🛠️ Technical Arsenal

**💻 Programming Languages**
[comma-separated list] \n

**🔧 Frameworks & Tools** 
[comma-separated list] \n

**⚡ Other Skills**
[comma-separated list] \n

---

## 💼 Experience Journey

### 🎯 [Job Title]
**[Company]** • *[Duration]* \n
• [Achievement/responsibility] \n
• [Achievement/responsibility] \n

---

## 🚀 Featured Projects

### 📦 [Project Name]
[Only include if repository provided: *[GitHub Repository](link)*]

🔹 [Project feature/description]
<br>
🔹 [Project feature/description]  
<br>
**🔧 Built with:** [technologies]

---

## 🎓 Education
\n
**[Degree]** \n
*[University]* • *[Years]* \n

---""",
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
