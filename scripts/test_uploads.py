from fastapi.testclient import TestClient
import app.main as app_main

client = TestClient(app_main.app)

# Prepare multiline resume text with escaped newlines for JSON
resume_text = ("PROFESSIONAL EXPERIENCE\n"
               "REVOCEPT SOLUTION PVT LTD\n"
               "Full Stack Web Developer 07/2023 to Current\n"
               "● Designed and implemented scalable microservices using ASP.NET Core, enhancing system\n"
               "modularity and maintainability.\n"
               "● Improved API response time by 30% through query optimization, indexing strategies, and\n"
               "performance tuning.\n"
               "SKILLS\n"
               "Frontend:\n"
               "● JavaScript (ES6+), React.js, Next.js, Redux, ASP.NET MVC, HTML5, Cascading\n"
               "Style Sheets (CSS3), Bootstrap, jQuery")

json_payload = {
    "text": resume_text,
    "description": "Shubham_resume"
}

print('Posting JSON to /upload/text...')
r = client.post('/upload/text', json=json_payload)
print('Status:', r.status_code)
print('Response:', r.json())

print('\nPosting raw multipart to /upload/text/raw...')
files = {
    'raw_text': ('resume.txt', resume_text, 'text/plain'),
    'filename': (None, 'Shubham_resume.txt')
}
r2 = client.post('/upload/text/raw', files=files)
print('Status:', r2.status_code)
print('Response:', r2.json())

# Quick query
print('\nQuerying /ask...')
q = {"question": "What is Python used for?", "top_k": 3}
r3 = client.post('/ask', json=q)
print('Status:', r3.status_code)
print('Response:', r3.json())
