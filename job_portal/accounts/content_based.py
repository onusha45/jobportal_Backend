import math


def read_pdf_manually(file_path):
    content = ""
    with open(file_path, "rb") as pdf_file:
        for line in pdf_file:
            if isinstance(line, bytes):
                content += line.decode("utf-8", errors="ignore")
    return content


def preprocess(text):
    return ''.join(char.lower() if char.isalnum() or char.isspace() else ' ' for char in text).split()


def compute_vector(document, keywords):
    doc_tokens = preprocess(document)
    return [doc_tokens.count(key) for key in keywords]


def cosine_similarity(vec1, vec2):
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(v1 ** 2 for v1 in vec1))
    magnitude2 = math.sqrt(sum(v2 ** 2 for v2 in vec2))
    return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0.0


def recommend_applicant(resume_path, job_factors):
    resume_content = read_pdf_manually(resume_path)

    keywords = preprocess(' '.join(job_factors.values()))

    resume_vector = compute_vector(resume_content, keywords)
    job_vector = compute_vector(' '.join(job_factors.values()), keywords)
    score = cosine_similarity(resume_vector, job_vector)

    return score


# job_data = {
#     "title": "Data Scientist",
#     "description": "Python, Machine Learning, AI, data analysis",
#     "experience": "3 years",
#     "salary": "100000",
#     "location": "New York",
#     "job_type": "fulltime"
# }

# resume_file = "applicant_resume.pdf"  # Provide a valid path to the PDF
# score = recommend_applicant(resume_
