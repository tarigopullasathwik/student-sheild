import validators
from PyPDF2 import PdfReader

def analyze_data(job_desc, email, website, file):
    score = 0
    reasons = []

    suspicious_keywords = [
        "registration fee",
        "processing fee",
        "urgent payment",
        "guaranteed job",
        "limited seats"
    ]

    # Check job description
    for word in suspicious_keywords:
        if word in job_desc.lower():
            score += 20
            reasons.append(f"Suspicious keyword detected: {word}")

    # Check email domain
    free_domains = ["gmail.com", "yahoo.com", "outlook.com"]
    for domain in free_domains:
        if domain in email.lower():
            score += 25
            reasons.append("Free email domain used")

    # Check website validity
    if not validators.url(website):
        score += 20
        reasons.append("Invalid website URL")

    # Check PDF content
    if file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        if "fee" in text.lower():
            score += 25
            reasons.append("Payment related content in offer letter")

    # Determine risk level
    if score > 70:
        risk = "HIGH"
    elif score >= 40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "score": score,
        "risk": risk,
        "reasons": reasons
    }