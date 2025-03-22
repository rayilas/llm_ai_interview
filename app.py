import os
import pdfplumber
import spacy
import nltk
from docx import Document
from flask import Flask, render_template, request

nltk.download('stopwords')

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load NLP Model
nlp = spacy.load("en_core_web_sm")

# Allowed file types
ALLOWED_EXTENSIONS = {"pdf", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_skills_and_experience(text):
    doc = nlp(text)
    skills = set()
    experience = []

    skill_keywords = {"python", "flask", "full stack development", "machine learning", "sql", "java", "html", "css", "javascript", "data analysis"}

    for token in doc:
        if token.text.lower() in skill_keywords:
            skills.add(token.text)

    for ent in doc.ents:
        if ent.label_ == "DATE" and "year" in ent.text.lower():
            experience.append(ent.text)

    return list(skills), experience

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        if "resume" not in request.files:
            return "Resume not found"
        
        file = request.files["resume"]
        if file.filename == "":
            return "No selected file"
        
        if file and allowed_file(file.filename):
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # Extract text
            extracted_text = ""
            if file.filename.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(filepath)
            elif file.filename.endswith(".docx"):
                extracted_text = extract_text_from_docx(filepath)
            else:
                return "Invalid file format. Allowed: pdf, docx"

            # Extract skills and experience
            skills, experience = extract_skills_and_experience(extracted_text)

            return render_template("result.html", text=extracted_text, skills=skills, experience=experience)

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
