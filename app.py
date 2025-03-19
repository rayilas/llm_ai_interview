import os
from flask import Flask , render_template, request 
app = Flask(__name__)  


#upload folder
Upload_folder="uploads"
app.config["Upload_folder"]=Upload_folder

Allowed_Extensions={"pdf","docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in Allowed_Extensions

@app.route('/') 
def home():
    return render_template("index.html")

@app.route("/upload",methods=["GET","POST"])
def upload_resume():
    if request.method == "POST":
        if "resume" not in request.files:
            return "Resume not found"
        file=request.files