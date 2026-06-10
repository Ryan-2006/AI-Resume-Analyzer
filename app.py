from flask import Flask, render_template, request
import pdfplumber
import os
import re

app = Flask(__name__)

# Upload Folder
UPLOAD_FOLDER = "resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Skills Database
skills_db = [
    "Python",
    "Java",
    "C++",
    "HTML",
    "CSS",
    "JavaScript",
    "SQL",
    "Flask",
    "Machine Learning",
    "Data Science",
    "Deep Learning",
    "Power BI",
    "Excel",
    "Tableau",
    "Pandas",
    "NumPy",
    "TensorFlow",
    "PyTorch",
    "OpenCV",
    "Git",
    "GitHub"
]


# Extract Text from PDF
def extract_text(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        if "resume" not in request.files:
            return render_template("index.html")

        file = request.files["resume"]

        if file.filename == "":
            return render_template("index.html")

        # Save Resume
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(file_path)

        # Extract Resume Text
        text = extract_text(file_path)

        # Email Detection
        email = re.findall(
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
            text
        )

        # Phone Detection
        phone = re.findall(
            r'\b\d{10}\b',
            text
        )

        # Skill Detection
        found_skills = []

        for skill in skills_db:

            if skill.lower() in text.lower():
                found_skills.append(skill)

        # ATS Score Calculation
        score = 0

        if email:
            score += 20

        if phone:
            score += 20

        score += len(found_skills) * 6

        if len(text) > 1000:
            score += 20

        score = min(score, 100)

        # Recommended Role
        role = "General Candidate"

        if "machine learning" in text.lower():
            role = "Machine Learning Engineer"

        elif "data science" in text.lower():
            role = "Data Scientist"

        elif "sql" in text.lower() and "python" in text.lower():
            role = "Data Analyst"

        elif "html" in text.lower() and "css" in text.lower():
            role = "Frontend Developer"

        elif "flask" in text.lower():
            role = "Python Developer"

        # Missing Skills
        desired_skills = [
            "Python",
            "SQL",
            "Power BI",
            "Excel",
            "Machine Learning"
        ]

        missing_skills = []

        for skill in desired_skills:

            if skill not in found_skills:
                missing_skills.append(skill)

        result = {
            "email": email[0] if email else "Not Found",
            "phone": phone[0] if phone else "Not Found",
            "skills": found_skills,
            "score": score,
            "role": role,
            "missing_skills": missing_skills
        }

    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True)