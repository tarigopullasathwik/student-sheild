from flask import Flask, request, jsonify, render_template
import pickle
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from docx import Document
import PyPDF2

app = Flask(__name__)
CORS(app)

# Load ML model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ ADD THIS BACK
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        sender_email = request.form.get("sender_email", "")
        company_email = request.form.get("company_email", "")
        description = request.form.get("text", "")

        file = request.files.get("offer_letter")
        file_text = ""
        uploaded_filename = ""

        if file:
            uploaded_filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_filename)
            file.save(file_path)

            if uploaded_filename.endswith(".pdf"):
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            file_text += page_text + "\n"

            elif uploaded_filename.endswith(".docx"):
                doc = Document(file_path)
                for para in doc.paragraphs:
                    if para.text:
                        file_text += para.text + "\n"

        combined_text = description + "\n" + file_text

        text_vectorized = vectorizer.transform([combined_text])
        prediction = model.predict(text_vectorized)[0]
        probability = model.predict_proba(text_vectorized)[0].max()

        if probability > 0.8:
            risk_level = "HIGH"
        elif probability > 0.5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return jsonify({
            "prediction": prediction,
            "confidence": round(float(probability) * 100, 2),
            "risk_level": risk_level,
            "sender_email": sender_email,
            "company_email": company_email,
            "uploaded_file": uploaded_filename
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)