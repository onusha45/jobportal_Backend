# accounts/content_based.py
import math
import sqlite3
from django.conf import settings
import os

def read_pdf_manually(file_path):
    """Read PDF file content manually"""
    content = ""
    try:
        with open(file_path, "rb") as pdf_file:
            for line in pdf_file:
                content += line.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return content

def preprocess(text):
    """Convert text to lowercase alphanumeric tokens and remove common stop words"""
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    tokens = ''.join(char.lower() if char.isalnum() or char.isspace() else ' ' for char in text).split()
    return [token for token in tokens if token not in stop_words]

def compute_tf(document_tokens):
    """Compute Term Frequency (TF) for a document"""
    tf = {}
    total_terms = len(document_tokens)
    for token in document_tokens:
        tf[token] = tf.get(token, 0) + 1 / total_terms
    return tf

def compute_idf(documents):
    """Compute Inverse Document Frequency (IDF) across a list of documents"""
    idf = {}
    total_docs = len(documents)
    for doc in documents:
        unique_tokens = set(doc)
        for token in unique_tokens:
            idf[token] = idf.get(token, 0) + 1
    for token in idf:
        idf[token] = math.log(total_docs / (1 + idf[token]))  # Add 1 to avoid division by zero
    return idf

def compute_vector(document_tokens, keywords, tf, idf):
    """Create TF-IDF vector for a document based on keywords"""
    return [tf.get(key, 0) * idf.get(key, 0) for key in keywords]

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(v1 ** 2 for v1 in vec1))
    magnitude2 = math.sqrt(sum(v2 ** 2 for v2 in vec2))
    return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0.0

def get_job_postings(db_path):
    """Fetch all job postings from SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, company_name, company_address, job_title, job_type, 
                   experience_level, job_description, requirements, 
                   min_salary, max_salary
            FROM accounts_jobposting
        """)
        jobs = []
        for row in cursor.fetchall():
            job = {
                'id': row[0],
                'company_name': row[1] or '',
                'company_address': row[2] or '',
                'job_title': row[3] or '',
                'job_type': row[4] or '',
                'experience_level': str(row[5]) if row[5] else '',
                'job_description': row[6] or '',
                'requirements': row[7] or '',
                'min_salary': str(row[8]) if row[8] else '',
                'max_salary': str(row[9]) if row[9] else ''
            }
            jobs.append(job)
        conn.close()
        return jobs
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_user_skills(db_path, user_id):
    """Fetch user skills and qualification from SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT skills, qualification 
            FROM accounts_customuser
            WHERE id = ?
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'skills': result[0] or '', 'qualification': result[1] or ''}
        return {'skills': '', 'qualification': ''}
    except Exception as e:
        print(f"Error fetching user skills: {e}")
        return {'skills': '', 'qualification': ''}

def recommend_jobs(resume_path, db_path, user_id=None):
    """Recommend jobs based on resume content and user profile using TF-IDF"""
    resume_content = read_pdf_manually(resume_path)
    if not resume_content:
        return []
    
    jobs = get_job_postings(db_path)
    if not jobs:
        return []
    
    user_profile = get_user_skills(db_path, user_id) if user_id else {'skills': '', 'qualification': ''}
    combined_content = resume_content + ' ' + user_profile['skills'] + ' ' + user_profile['qualification']
    resume_tokens = preprocess(combined_content)
    
    # Prepare job documents
    job_docs = []
    for job in jobs:
        job_text = ' '.join(str(value) for value in job.values() if value)
        job_docs.append(preprocess(job_text))
    
    # Compute TF-IDF
    all_docs = [resume_tokens] + job_docs
    idf = compute_idf(all_docs)
    resume_tf = compute_tf(resume_tokens)
    keywords = list(idf.keys())  # Use all unique terms as keywords
    resume_vector = compute_vector(resume_tokens, keywords, resume_tf, idf)
    
    recommendations = []
    for job, job_tokens in zip(jobs, job_docs):
        job_tf = compute_tf(job_tokens)
        job_vector = compute_vector(job_tokens, keywords, job_tf, idf)
        similarity = cosine_similarity(resume_vector, job_vector)
        
        # Bonus for exact skill matches
        if user_profile['skills']:
            skill_matches = sum(1 for skill in preprocess(user_profile['skills']) 
                              if skill in preprocess(job['requirements'] + ' ' + job['job_description']))
            similarity += skill_matches * 0.1
        
        # Bonus for exact phrase matches (e.g., "machine learning")
        resume_text = ' '.join(resume_tokens)
        job_text = ' '.join(job_tokens)
        phrase_bonus = sum(1 for phrase in preprocess(user_profile['skills']) if phrase in job_text and phrase in resume_text) * 0.05
        
        final_score = min(similarity + phrase_bonus, 1.0)
        recommendations.append((job['id'], final_score))
    
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations

def get_top_recommendations(resume_path, user_id=None, top_n=5):
    """Get top N job recommendations"""
    db_path = str(settings.DATABASES['default']['NAME'])
    return recommend_jobs(resume_path, db_path, user_id)[:top_n]