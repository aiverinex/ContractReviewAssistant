#!/usr/bin/env python3
"""
Contract Reviewer Crew - Web Application

A Flask-based web interface for the AI-powered contract review system.
Provides an intuitive UI for uploading contracts and viewing analysis results.
"""

import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_cors import CORS

# Import the contract review system
from main import (
    load_environment, 
    load_config, 
    extract_text_from_pdf, 
    extract_text_from_docx,
    save_review_results
)
from crew.crew import ContractReviewCrew

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    """Extract text from uploaded file based on extension with OCR support."""
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        # Handle image files directly with OCR
        try:
            from utils.ocr_handler import ocr_handler
            return ocr_handler.extract_text_from_image(file_path)
        except Exception as e:
            raise ValueError(f"OCR extraction failed: {str(e)}")
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

@app.route('/')
def index():
    """Main page with file upload interface."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and contract analysis."""
    try:
        # Check if file was uploaded
        if 'contract_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['contract_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Please upload .txt, .pdf, or .docx files'}), 400
        
        # Save uploaded file
        if file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
        else:
            return jsonify({'error': 'Invalid filename'}), 400
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text from file
        try:
            contract_text = extract_text_from_file(file_path)
            if not contract_text.strip():
                return jsonify({'error': 'Could not extract text from the file'}), 400
        except Exception as e:
            return jsonify({'error': f'Failed to process file: {str(e)}'}), 400
        
        # Initialize and run contract review
        try:
            crew = ContractReviewCrew()
            results = crew.review_contract(contract_text)
            
            if not results.get('success'):
                return jsonify({'error': f"Analysis failed: {results.get('error', 'Unknown error')}"}), 500
            
            # Save results
            save_review_results(results)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'results': results,
                'filename': file.filename
            })
            
        except Exception as e:
            return jsonify({'error': f'Contract analysis failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500



@app.route('/results/<result_id>')
def view_results(result_id):
    """View detailed results page."""
    return render_template('results.html', result_id=result_id)

@app.route('/download/<filename>')
def download_report(filename):
    """Download a specific report file."""
    try:
        output_dir = Path("output")
        file_path = output_dir / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/download/latest')
def download_latest_report():
    """Download the most recent report as a professional PDF."""
    try:
        output_dir = Path("output")
        if not output_dir.exists():
            return jsonify({'error': 'No reports available'}), 404
        
        # Find the most recent JSON file
        json_files = list(output_dir.glob("review_summary_*.json"))
        if not json_files:
            return jsonify({'error': 'No reports found'}), 404
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        # Load the results data
        with open(latest_file, 'r', encoding='utf-8') as file:
            results = json.load(file)
        
        # Generate professional PDF report
        from utils.pdf_report_generator import pdf_generator
        pdf_path = pdf_generator.generate_report(results)
        
        return send_file(pdf_path, as_attachment=True, download_name='contract_analysis_report.pdf')
        
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """Check API and system status."""
    try:
        # Check if environment is loaded
        openai_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize crew to check status
        crew = ContractReviewCrew()
        status = crew.get_crew_status()
        
        return jsonify({
            'status': 'healthy',
            'openai_configured': bool(openai_key),
            'crew_ready': status.get('crew_initialized', False),
            'agents_available': status.get('agents_available', {})
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'openai_configured': False,
            'crew_ready': False
        }), 500

if __name__ == '__main__':
    # Load environment
    try:
        load_environment()
        print("✅ Web application starting...")
        print("🌐 Access the Contract Reviewer at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start web application: {e}")
        print(f"Full error: {traceback.format_exc()}")