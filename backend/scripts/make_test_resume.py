"""Generate a realistic sample PDF resume via HTML rendering for clean text extraction."""
import os
import fitz

OUT = os.path.join(os.getcwd(), "uploads", "sampleresume_test.pdf")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

HTML = """
<h1>Rohan Mehta</h1>
<p><b>Senior Python Backend Engineer</b></p>
<p>+91 98765 43210 &nbsp;|&nbsp; rohan.mehta@example.com &nbsp;|&nbsp; Bengaluru, India</p>

<h2>PROFILE</h2>
<p>Backend engineer with 6+ years of experience building high-traffic REST APIs and microservices.
Experienced with Python, FastAPI, Django, PostgreSQL, Redis, Docker, and AWS.
Led a team of 4 engineers and mentored junior developers.</p>

<h2>SKILLS</h2>
<p>Python, FastAPI, Django, PostgreSQL, Redis, Celery, Docker, Kubernetes, AWS, REST API, SQL,
Git, CI/CD, pytest, RabbitMQ, GraphQL, Kafka</p>

<h2>EXPERIENCE</h2>
<p><b>Senior Backend Engineer | TechNova Solutions | 2022 - Present</b></p>
<p>Built and shipped scalable payment APIs serving 2M+ users. Reduced API latency by 40% using
Redis caching and query optimization. Owned architecture of 6 microservices deployed on AWS ECS
and Kubernetes.</p>
<p><b>Backend Developer | DataWorks | 2019 - 2022</b></p>
<p>Developed Django and PostgreSQL services for an analytics product. Designed REST APIs, wrote
500+ unit tests, and set up CI/CD pipelines with GitHub Actions.</p>

<h2>EDUCATION</h2>
<p>B.Tech in Computer Science, IIT Delhi, 2015 - 2019</p>
"""

doc = fitz.open()
page = doc.new_page()
rect = fitz.Rect(40, 34, 555, 800)
page.insert_htmlbox(rect, HTML, scale_low=0.8)
doc.save(OUT)
doc.close()

doc2 = fitz.open(OUT)
extracted = doc2[0].get_text()
doc2.close()
print(f"PDF saved: {OUT}")
print("--- extracted lines ---")
for line in extracted.splitlines():
    print(f"   |{line.rstrip()}|")