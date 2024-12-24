import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

# Load the dataset
def load_data():
    # Load the CSV file and drop rows with missing critical columns
    data = pd.read_csv('data/job_descriptions.csv')  # Update path if needed
    return data

# Clean text data by removing stopwords and unnecessary characters
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()  # Convert to lowercase
    text = ''.join(e for e in text if e.isalnum() or e.isspace())  # Remove special characters
    return ' '.join([word for word in text.split() if word not in stop_words])  # Remove stopwords

# Filter jobs based on user inputs
def filter_jobs(jobs, job_title=None, country=None, skills=None):
    filtered_jobs = jobs.copy()

    # Filter by Job Title
    if job_title:
        filtered_jobs = filtered_jobs[filtered_jobs['Job Title'].str.lower().str.contains(job_title.lower(), na=False)]

    # Filter by Country/Location
    if country:
        filtered_jobs = filtered_jobs[filtered_jobs['Country'].str.lower().str.contains(country.lower(), na=False)]

    # Filter by Skills (multiple skills allowed)
    if skills:
        skills_list = [skill.strip().lower() for skill in skills.split(',')]  # Assuming skills input is comma-separated
        filtered_jobs = filtered_jobs[filtered_jobs['skills'].str.lower().apply(
            lambda x: any(skill in x for skill in skills_list)
        )]

    return filtered_jobs

# Recommend jobs based on user input
def recommend_jobs(filtered_data, user_input):
    # Combine features for recommendation
    filtered_data['combined_features'] = (
        filtered_data['Job Title'].fillna('') + ' ' +
        filtered_data['Job Description'].fillna('') + ' ' +
        filtered_data['skills'].fillna('') + ' ' +
        filtered_data['Company'].fillna('') + ' ' +
        filtered_data['Experience'].fillna('') + ' ' +
        filtered_data['Salary Range'].fillna('')
    )

    # Vectorize the combined features
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(filtered_data['combined_features'])

    # Transform user input (job title, skills, etc.) to a vector using the same TF-IDF vectorizer
    user_input_tfidf = tfidf.transform([user_input])

    # Compute cosine similarity between user input and job descriptions
    cosine_sim = cosine_similarity(user_input_tfidf, tfidf_matrix)

    # Get the indices of the top N recommended jobs based on cosine similarity score
    sim_scores = list(enumerate(cosine_sim[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Filter the jobs based on similarity score threshold (e.g., >= 0.1)
    recommended_job_indices = [job[0] for job in sim_scores if job[1] > 0.1]  # Adjust the threshold as necessary

    # Get the recommended jobs and return them
    recommended_jobs = filtered_data.iloc[recommended_job_indices]

    return recommended_jobs[['Job Title', 'Role','Job Description', 'Company', 'Experience', 'Salary Range', 'skills']]





# <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">