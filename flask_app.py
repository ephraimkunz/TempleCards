
from flask import Flask, request, send_file, render_template, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from pathlib import Path
from cards import convert_pdf

THIS_FOLDER = Path(__file__).parent.resolve()

# Directory to save uploaded and processed files
UPLOAD_FOLDER = THIS_FOLDER / "uploads"
RESULT_FOLDER = THIS_FOLDER / "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            flash("No file part in the request.", "danger")
            return redirect(url_for("index"))

        file = request.files["file"]

        if file.filename == "":
            flash("No selected file. Please upload a PDF.", "warning")
            return redirect(url_for("index"))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_pdf_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_pdf_path)

            # Process the uploaded PDF
            output_pdf_path = os.path.join(RESULT_FOLDER, f"processed_{filename}")
            success = convert_pdf(input_pdf_path, output_pdf_path)
            if success:
                return send_file(output_pdf_path, as_attachment=True)
            else:
                flash("Error processing PDF, no bounding boxes shown.", "danger")
                return redirect(url_for("index"))
        else:
            flash("Invalid file type. Only PDFs are allowed.", "warning")
            return redirect(url_for("index"))

    except Exception as e:
        # Log the error for debugging (optional)
        print(f"Error: {e}")
        flash("An unexpected error occurred. Please try again.", "danger")
        return redirect(url_for("index"))