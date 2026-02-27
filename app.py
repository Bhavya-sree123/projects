from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔴 PUT YOUR REAL ADZUNA API KEYS HERE
ADZUNA_APP_ID = "your_app_id"
ADZUNA_APP_KEY = "your_app_key"


# --------------------------
# Probability Logic
# --------------------------
def calculate_probability(cgpa, projects, internship, skills):

    probability = ((cgpa/10)*30) + (projects*5) + (internship*20) + (skills*5)
    probability = min(probability, 100)

    if probability < 50:
        suggestions = ["Improve DSA", "Build 2 Projects", "Improve Communication"]
        roadmap = ["Week 1: Basics", "Week 2: Practice Coding", "Week 3: Mini Project"]
    else:
        suggestions = ["Apply for Internships", "Mock Interviews", "Target Product Companies"]
        roadmap = ["Advanced DSA", "System Design Basics", "Interview Practice"]

    return round(probability,2), suggestions, roadmap


# --------------------------
# Fetch Jobs
# --------------------------
def get_jobs(keyword, location):

    url = "https://api.adzuna.in/v1/api/jobs/in/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": keyword,
        "where": location,
        "results_per_page": 5
    }

    jobs = []

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "results" in data:
            for job in data["results"]:
                jobs.append({
                    "title": job["title"],
                    "company": job["company"]["display_name"],
                    "location": job["location"]["display_name"],
                    "salary": job.get("salary_text", "Not specified"),
                    "url": job["redirect_url"]
                })
    except:
        jobs = []

    if not jobs:
        jobs = [{
            "title": "No jobs found",
            "company": "",
            "location": "",
            "salary": "",
            "url": "#"
        }]

    return jobs


# --------------------------
# MAIN ROUTE (HTML INSIDE PYTHON)
# --------------------------
@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Career AI System</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{font-family:Arial;background:#1e1e2f;color:white;text-align:center;padding:20px;}
input,select{padding:8px;margin:5px;width:200px;}
button{padding:10px;margin-top:10px;background:#00ffd5;border:none;cursor:pointer;}
.job{background:#333;padding:10px;margin:5px;border-radius:8px;}
</style>
</head>
<body>

<h2>🚀 Career AI Predictor</h2>

<input type="number" id="cgpa" placeholder="CGPA (0-10)" step="0.1"><br>
<input type="number" id="projects" placeholder="Projects"><br>

<select id="internship">
<option value="1">Internship - Yes</option>
<option value="0">Internship - No</option>
</select><br>

<input type="number" id="skills" placeholder="Skill Level (1-10)"><br>
<input type="text" id="location" placeholder="Location (Hyderabad)"><br>

<button onclick="analyze()">Analyze</button>

<div id="result"></div>
<canvas id="chart" width="200" height="200"></canvas>

<script>
let myChart;

async function analyze(){

const cgpa=document.getElementById("cgpa").value;
const projects=document.getElementById("projects").value;
const internship=document.getElementById("internship").value;
const skills=document.getElementById("skills").value;
const location=document.getElementById("location").value || "India";

if(cgpa==""||projects==""||skills==""){
alert("Fill all fields");
return;
}

document.getElementById("result").innerHTML="Analyzing...";

const response=await fetch("/analyze",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({cgpa,projects,internship,skills,location})
});

const data=await response.json();

document.getElementById("result").innerHTML=`
<h3>Probability: ${data.probability}%</h3>
<h4>Suggestions</h4>
${data.suggestions.join("<br>")}
<h4>Roadmap</h4>
${data.roadmap.join("<br>")}
<h4>Jobs</h4>
${data.jobs.map(j=>`
<div class="job">
<b>${j.title}</b><br>
${j.company}<br>
${j.location}<br>
${j.salary}<br>
<a href="${j.url}" target="_blank">
<button>Apply</button>
</a>
</div>
`).join("")}
`;

if(myChart) myChart.destroy();

myChart=new Chart(document.getElementById("chart"),{
type:"doughnut",
data:{
labels:["Success","Risk"],
datasets:[{data:[data.probability,100-data.probability]}]
}
});

}
</script>

</body>
</html>
"""


@app.route("/analyze", methods=["POST"])
def analyze():

    data=request.json

    cgpa=float(data["cgpa"])
    projects=float(data["projects"])
    internship=float(data["internship"])
    skills=float(data["skills"])
    location=data["location"]

    probability,suggestions,roadmap=calculate_probability(
        cgpa,projects,internship,skills
    )

    keyword="Python Developer" if skills<7 else "Full Stack Developer"

    jobs=get_jobs(keyword,location)

    return jsonify({
        "probability":probability,
        "suggestions":suggestions,
        "roadmap":roadmap,
        "jobs":jobs
    })


if __name__=="__main__":
    app.run(debug=True)