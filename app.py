from flask import Flask, render_template, request
import pandas as pd
from models.job_recommender import filter_jobs, recommend_jobs, load_data, clean_text

# Create Flask app instance
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Retrieve user inputs
            job_title = request.form.get('job_title', "").strip()
            country = request.form.get('country', "").strip()
            skills = request.form.get('skills', "").strip()  # New input for skills

            # Validate inputs
            if not job_title and not country:
                return render_template('index.html', recommended_jobs=None, message="Please provide at least one input (Job Title or Country).")

            # Load the job dataset
            data = load_data()

            # Filter the data based on the user's inputs
            filtered_jobs = filter_jobs(data, job_title=clean_text(job_title), country=clean_text(country), skills=clean_text(skills))
            print(f"Filtered Jobs Count: {len(filtered_jobs)}")

            if filtered_jobs.empty:
                return render_template('index.html', recommended_jobs=None, message="No matching jobs found. Please refine your search.")

            # Combine relevant features for recommendation
            pd.options.mode.chained_assignment = None  # Disable chained assignment warnings temporarily
            filtered_jobs['combined_features'] = (
                filtered_jobs['Job Title'].fillna('') + ' ' +
                filtered_jobs['Job Description'].fillna('') + ' ' +
                filtered_jobs['skills'].fillna('') + ' ' +
                filtered_jobs['Company'].fillna('') + ' ' +
                filtered_jobs['Experience'].fillna('') + ' ' +
                filtered_jobs['Salary Range'].fillna('')
            )

            # Get job recommendations
            recommended_jobs = recommend_jobs(filtered_jobs, clean_text(job_title))

            # If no recommendations are found, return a message
            if recommended_jobs.empty:
                return render_template('index.html', recommended_jobs=None, message="No suitable job recommendations found.")

            # Return the filtered job recommendations to the template
            return render_template(
                'index.html',
                recommended_jobs=recommended_jobs.to_html(classes='table table-bordered', index=False),
                message=None
            )

        except Exception as e:
            print(f"Error: {e}")
            # Handle any errors that occur and display an error message
            return render_template('index.html', recommended_jobs=None, message=f"An error occurred: {str(e)}")

    # For the first page load
    return render_template('index.html', recommended_jobs=None, message=None)

if __name__ == '__main__':
    app.run(debug=True)
