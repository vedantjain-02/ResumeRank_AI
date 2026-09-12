"""
Hand-crafted candidate profiles for seeding (new JSONB schema).
50 profiles; run_seed.py generates the remaining 50 to reach 100.

Keys map exactly to the Candidate model columns.
"""

CANDIDATES = [
    {
        "name": "Aarav Sharma", "phone_number": "+91 98765 43210",
        "career_summary": "Senior backend engineer with 7 years of experience building scalable microservices and REST APIs in the fintech space. Proficient in Python, FastAPI, and PostgreSQL with deep experience in containerized deployments and event-driven architecture.",
        "total_experience_years": 7, "seniority_level": "Senior",
        "job_title": "Senior Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "REST APIs, microservices, event-driven systems", "years": 7},
            {"area": "Cloud & Infrastructure", "details": "AWS ECS, Docker, Kubernetes", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "IIT Mumbai", "graduation_year": 2016}
        ],
        "capability_tags": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Redis", "SQL", "Git", "Celery", "RabbitMQ", "AWS", "CI/CD"],
    },
    {
        "name": "Priya Patel", "phone_number": "+91 87654 32109",
        "career_summary": "Data scientist with 5 years of experience in the healthcare domain. Specialized in building and deploying machine learning models for patient outcome prediction using Python, TensorFlow, and Scikit-learn.",
        "total_experience_years": 5, "seniority_level": "Mid-Level",
        "job_title": "Data Scientist",
        "functional_expertise": [
            {"area": "Data Science", "details": "Predictive modeling, feature engineering", "years": 5},
            {"area": "Machine Learning", "details": "Classification, regression, NLP", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.S.", "field": "Data Science", "institution": "Stanford University", "graduation_year": 2019}
        ],
        "capability_tags": ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Matplotlib", "SQL", "Statistics", "Machine Learning", "Data Visualization", "PyTorch"],
    },
    {
        "name": "Vikram Singh", "phone_number": "+91 98712 34567",
        "career_summary": "Lead Java architect with 9 years of experience designing enterprise-grade microservices for BFSI clients. Deep expertise in Spring Boot, Kafka, and distributed systems.",
        "total_experience_years": 9, "seniority_level": "Lead",
        "job_title": "Lead Java Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Java microservices, Kafka, distributed transactions", "years": 9},
            {"area": "System Design", "details": "High-availability architecture", "years": 5},
        ],
        "leadership": {"has_leadership": True, "roles": ["Tech Lead", "Code Reviewer"], "team_size": 6, "responsibilities": ["Architecture design", "Code reviews", "Mentoring junior developers"]},
        "education": [
            {"degree": "B.E.", "field": "Information Technology", "institution": "VJTI Mumbai", "graduation_year": 2015}
        ],
        "capability_tags": ["Java", "Spring", "Spring Boot", "Hibernate", "MySQL", "PostgreSQL", "Microservices", "REST API", "Kafka", "Maven", "Git", "Docker"],
    },
    {
        "name": "Ananya Verma", "phone_number": "+91 76543 21098",
        "career_summary": "Frontend specialist with 4 years of experience building responsive, accessible web applications using React and TypeScript. Strong eye for UI/UX and component-driven development.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "Frontend Developer",
        "functional_expertise": [
            {"area": "Frontend Development", "details": "React, TypeScript, component libraries", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "BCA", "field": "Computer Applications", "institution": "Delhi University", "graduation_year": 2020}
        ],
        "capability_tags": ["JavaScript", "TypeScript", "React", "Angular", "Vue", "HTML", "CSS", "Sass", "Webpack", "Jest", "Redux", "Git"],
    },
    {
        "name": "Rahul Gupta", "phone_number": "+91 65432 10987",
        "career_summary": "Senior DevOps engineer with 8 years of experience building CI/CD pipelines, container orchestration, and infrastructure-as-code for SaaS platforms at scale.",
        "total_experience_years": 8, "seniority_level": "Senior",
        "job_title": "Senior DevOps Engineer",
        "functional_expertise": [
            {"area": "DevOps", "details": "CI/CD, Terraform, Kubernetes", "years": 8},
            {"area": "Cloud & Infrastructure", "details": "AWS, Azure, GCP", "years": 6},
        ],
        "leadership": {"has_leadership": True, "roles": ["DevOps Lead"], "team_size": 4, "responsibilities": ["Platform reliability", "Incident response planning"]},
        "education": [
            {"degree": "B.Tech", "field": "Electronics", "institution": "NIT Trichy", "graduation_year": 2016}
        ],
        "capability_tags": ["Docker", "Kubernetes", "AWS", "Azure", "Terraform", "Ansible", "Jenkins", "Linux", "CI/CD", "Python", "Bash", "Prometheus", "Grafana", "Git"],
    },
    {
        "name": "Sneha Reddy", "phone_number": "+91 54321 09876",
        "career_summary": "Machine learning engineer with 6 years of experience deploying production ML pipelines for healthcare imaging. Proficient in PyTorch, TensorFlow, MLOps, and Kubernetes.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Machine Learning Engineer",
        "functional_expertise": [
            {"area": "Machine Learning", "details": "Computer vision, NLP, MLOps", "years": 6},
            {"area": "Cloud & Infrastructure", "details": "AWS SageMaker, Kubernetes", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.S.", "field": "Artificial Intelligence", "institution": "Carnegie Mellon University", "graduation_year": 2018}
        ],
        "capability_tags": ["Python", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Docker", "Kubernetes", "MLOps", "AWS", "NLP", "Computer Vision", "SQL", "Git"],
    },
    {
        "name": "Karan Mehta", "phone_number": "+91 43210 98765",
        "career_summary": "Full-stack software engineer with 3 years of experience shipping user-facing features at a fast-paced edtech startup. Comfortable with both frontend and backend development.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Software Engineer",
        "functional_expertise": [
            {"area": "Frontend Development", "details": "React, TypeScript", "years": 2},
            {"area": "Backend Development", "details": "Node.js, PostgreSQL", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "IIIT Hyderabad", "graduation_year": 2021}
        ],
        "capability_tags": ["JavaScript", "Python", "TypeScript", "React", "Node.js", "SQL", "Docker", "Git", "REST API", "Algorithm Design", "Data Structures"],
    },
    {
        "name": "Divya Iyer", "phone_number": "+91 32109 87654",
        "career_summary": "Data analyst with 4 years of experience in retail analytics. Expert in SQL, Power BI, and Tableau with strong business acumen for translating data into actionable insights.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "Data Analyst",
        "functional_expertise": [
            {"area": "Data Analytics", "details": "BI dashboards, KPI tracking", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Sc", "field": "Statistics", "institution": "University of Mumbai", "graduation_year": 2020}
        ],
        "capability_tags": ["SQL", "Python", "Pandas", "Excel", "Power BI", "Tableau", "Statistics", "Data Visualization", "R", "NumPy"],
    },
    {
        "name": "Amit Sharma", "phone_number": "+91 21098 76543",
        "career_summary": "Cloud infrastructure engineer with 6 years of experience designing and maintaining multi-cloud environments on AWS and Azure. Certified solutions architect with strong networking fundamentals.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Cloud Engineer",
        "functional_expertise": [
            {"area": "Cloud & Infrastructure", "details": "AWS, Azure, Terraform, networking", "years": 6},
            {"area": "DevOps", "details": "CI/CD, IaC", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Electronics & Communication", "institution": "NIT Warangal", "graduation_year": 2018}
        ],
        "capability_tags": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "Linux", "Networking", "Python", "Bash", "CI/CD", "IaaS"],
    },
    {
        "name": "Neha Kulkarni", "phone_number": "+91 10987 65432",
        "career_summary": "Backend developer with 5 years of experience building Django and FastAPI services for edtech platforms. Strong background in PostgreSQL, Redis caching, and background task processing.",
        "total_experience_years": 5, "seniority_level": "Mid-Level",
        "job_title": "Python Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Django, FastAPI, PostgreSQL", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Sc", "field": "Computer Science", "institution": "Pune University", "graduation_year": 2019}
        ],
        "capability_tags": ["Python", "Django", "Flask", "FastAPI", "PostgreSQL", "Redis", "Docker", "REST API", "SQL", "Celery", "RabbitMQ", "Gunicorn", "Git"],
    },
    {
        "name": "Rohan Joshi", "phone_number": "+91 09876 54321",
        "career_summary": "Senior full-stack developer with 7 years of experience delivering end-to-end features for SaaS products. Proficient in React, Node.js, Python, and PostgreSQL.",
        "total_experience_years": 7, "seniority_level": "Senior",
        "job_title": "Full Stack Developer",
        "functional_expertise": [
            {"area": "Full Stack Development", "details": "React, Node.js, Python, PostgreSQL", "years": 7},
            {"area": "Cloud & Infrastructure", "details": "AWS, Docker", "years": 4},
        ],
        "leadership": {"has_leadership": True, "roles": ["Tech Lead"], "team_size": 4, "responsibilities": ["Sprint planning", "Technical mentoring"]},
        "education": [
            {"degree": "MCA", "field": "Computer Applications", "institution": "BHU", "graduation_year": 2017}
        ],
        "capability_tags": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "Django", "PostgreSQL", "MongoDB", "HTML", "CSS", "Docker", "REST API", "Git", "GraphQL"],
    },
    {
        "name": "Kavya Nair", "phone_number": "+91 98711 22334",
        "career_summary": "Junior data analyst with 2 years of experience in healthcare analytics. Skilled in SQL, Python, and Tableau with a strong foundation in statistical analysis.",
        "total_experience_years": 2, "seniority_level": "Junior",
        "job_title": "Data Analyst",
        "functional_expertise": [
            {"area": "Data Analytics", "details": "Healthcare analytics, reporting", "years": 2},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Sc", "field": "Statistics", "institution": "Kerala University", "graduation_year": 2022}
        ],
        "capability_tags": ["Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Statistics", "Data Visualization", "Matplotlib", "Machine Learning"],
    },
    {
        "name": "Siddharth Patil", "phone_number": "+91 11223 34455",
        "career_summary": "Java backend developer with 5 years of experience building microservices for banking clients. Strong in Spring Boot, Kafka, and PostgreSQL with performance optimization skills.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Java Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Java microservices, Kafka, transaction management", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.E.", "field": "Information Technology", "institution": "COEP Pune", "graduation_year": 2019}
        ],
        "capability_tags": ["Java", "Spring Boot", "Microservices", "REST API", "PostgreSQL", "MySQL", "Docker", "Kafka", "Maven", "Git"],
    },
    {
        "name": "Ritika Kapoor", "phone_number": "+91 22334 45566",
        "career_summary": "Frontend developer with 3 years of experience building e-commerce web interfaces with React. Strong CSS and accessibility skills.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Frontend Developer",
        "functional_expertise": [
            {"area": "Frontend Development", "details": "React, Redux, responsive design", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "JNU Delhi", "graduation_year": 2021}
        ],
        "capability_tags": ["JavaScript", "CSS", "Sass", "HTML", "Webpack", "Jest", "Git", "React", "Redux"],
    },
    {
        "name": "Varun Malhotra", "phone_number": "+91 33445 56677",
        "career_summary": "DevOps and platform engineer with 6 years of experience automating infrastructure for telecom and SaaS companies. Proficient in Kubernetes, Jenkins, and Terraform.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Platform Engineer",
        "functional_expertise": [
            {"area": "DevOps", "details": "Jenkins, Kubernetes, Terraform, Ansible", "years": 6},
            {"area": "Cloud & Infrastructure", "details": "AWS, Linux", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.E.", "field": "Electrical Engineering", "institution": "DTU", "graduation_year": 2018}
        ],
        "capability_tags": ["Docker", "Kubernetes", "Jenkins", "Linux", "Bash", "CI/CD", "Python", "Ansible", "Terraform", "AWS", "Prometheus", "Grafana", "Git"],
    },
    {
        "name": "Anjali Saxena", "phone_number": "+91 44556 67788",
        "career_summary": "Machine learning engineer with 4 years of experience building NLP and computer vision models for media content analysis. Skilled in PyTorch and MLOps.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "ML Engineer",
        "functional_expertise": [
            {"area": "Machine Learning", "details": "NLP, Computer Vision, model deployment", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.S.", "field": "Artificial Intelligence", "institution": "IIIT Bangalore", "graduation_year": 2020}
        ],
        "capability_tags": ["Python", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Scikit-learn", "SQL", "Docker", "Git"],
    },
    {
        "name": "Aditya Chopra", "phone_number": "+91 55667 78899",
        "career_summary": "Full-stack developer with 5 years of experience delivering edtech products. Expertise in React, Node.js, PostgreSQL, and GraphQL API design.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Full Stack Developer",
        "functional_expertise": [
            {"area": "Full Stack Development", "details": "React, Node.js, GraphQL", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "Thapar University", "graduation_year": 2019}
        ],
        "capability_tags": ["JavaScript", "TypeScript", "Node.js", "React", "Python", "PostgreSQL", "MongoDB", "GraphQL", "Docker", "Git", "REST API"],
    },
    {
        "name": "Sneha Iyer", "phone_number": "+91 66778 89900",
        "career_summary": "Junior frontend developer with 2 years of experience building Angular and Vue applications for media companies. Strong in HTML/CSS and unit testing.",
        "total_experience_years": 2, "seniority_level": "Junior",
        "job_title": "Frontend Developer",
        "functional_expertise": [
            {"area": "Frontend Development", "details": "Angular, Vue, responsive UI", "years": 2},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Sc", "field": "Computer Science", "institution": "Loyola College Chennai", "graduation_year": 2022}
        ],
        "capability_tags": ["JavaScript", "Angular", "Vue", "HTML", "CSS", "TypeScript", "Redux", "Jest", "Git"],
    },
    {
        "name": "Aditya Reddy", "phone_number": "+91 77889 90011",
        "career_summary": "Data scientist with 6 years of experience in logistics optimization. Expert in Python, predictive modeling, and data visualization with a strong operations research background.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Data Scientist",
        "functional_expertise": [
            {"area": "Data Science", "details": "Predictive modeling, operations research", "years": 6},
            {"area": "Machine Learning", "details": "Time-series forecasting, optimization", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Tech", "field": "Computer Science", "institution": "IIT Madras", "graduation_year": 2018}
        ],
        "capability_tags": ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Machine Learning", "Statistics", "SQL", "Data Visualization"],
    },
    {
        "name": "Mohit Sethi", "phone_number": "+91 88990 01122",
        "career_summary": "Backend and platform engineer with 6 years of experience building high-throughput Python services for fintech. Proficient in FastAPI, PostgreSQL, Redis, Kafka, and Kubernetes.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Backend Engineer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "FastAPI, PostgreSQL, event-driven systems", "years": 6},
            {"area": "Cloud & Infrastructure", "details": "AWS, Kubernetes", "years": 3},
        ],
        "leadership": {"has_leadership": True, "roles": ["Tech Lead"], "team_size": 3, "responsibilities": ["Architecture reviews", "Mentoring"]},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "DTU", "graduation_year": 2018}
        ],
        "capability_tags": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "SQL", "Git", "REST API", "AWS", "Celery", "Kafka", "Kubernetes"],
    },
    {
        "name": "Aarav Patel", "phone_number": "+91 99001 12233",
        "career_summary": "Java developer with 3 years of experience building REST APIs for telecom clients. Solid understanding of Spring Boot and database design.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Java Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Java, Spring Boot, REST APIs", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "VIT Vellore", "graduation_year": 2021}
        ],
        "capability_tags": ["Java", "Spring Boot", "MySQL", "PostgreSQL", "REST API", "Microservices", "Git", "Maven"],
    },
    {
        "name": "Meera Nair", "phone_number": "+91 10012 23344",
        "career_summary": "Machine learning engineer with 5 years of experience in healthcare NLP and computer vision. Experienced with PyTorch, TensorFlow, and production ML pipelines on AWS.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Machine Learning Engineer",
        "functional_expertise": [
            {"area": "Machine Learning", "details": "NLP, Computer Vision, MLOps", "years": 5},
            {"area": "Data Science", "details": "Healthcare analytics", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.S.", "field": "Artificial Intelligence", "institution": "Georgia Tech", "graduation_year": 2019}
        ],
        "capability_tags": ["Python", "PyTorch", "TensorFlow", "Keras", "NLP", "Computer Vision", "Scikit-learn", "Docker", "Git", "SQL", "MLOps", "AWS"],
    },
    {
        "name": "Kavya Sharma", "phone_number": "+91 21123 34455",
        "career_summary": "Business analyst and data analyst with 3 years of experience in retail analytics. Proficient in SQL, Power BI, and Excel-based reporting.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Data Analyst",
        "functional_expertise": [
            {"area": "Data Analytics", "details": "BI reporting, sales analytics", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Com", "field": "Commerce", "institution": "SRCC Delhi", "graduation_year": 2021}
        ],
        "capability_tags": ["SQL", "Excel", "Power BI", "Tableau", "Python", "Pandas", "Statistics", "Data Visualization"],
    },
    {
        "name": "Vivek Kumar", "phone_number": "+91 32234 45566",
        "career_summary": "Python backend developer with 4 years of experience building Flask and Django applications for edtech. Strong in PostgreSQL and Redis caching.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Django, Flask, PostgreSQL", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "BCA", "field": "Computer Applications", "institution": "IP University Delhi", "graduation_year": 2020}
        ],
        "capability_tags": ["Python", "Django", "Flask", "PostgreSQL", "MySQL", "Docker", "REST API", "Redis", "SQL", "Celery", "Git"],
    },
    {
        "name": "Shreya Menon", "phone_number": "+91 43345 56677",
        "career_summary": "Frontend developer with 3 years of experience building React and TypeScript interfaces for media products. Skilled in Redux, Jest, and GraphQL.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Frontend Developer",
        "functional_expertise": [
            {"area": "Frontend Development", "details": "React, TypeScript, Redux", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "Amrita Vishwa Vidyapeetham", "graduation_year": 2021}
        ],
        "capability_tags": ["JavaScript", "React", "TypeScript", "Node.js", "CSS", "HTML", "Jest", "Git", "Redux", "GraphQL"],
    },
    {
        "name": "Arjun Chopra", "phone_number": "+91 54456 67788",
        "career_summary": "Cloud architect with 7 years of experience on AWS, Azure, and GCP. Certified Kubernetes administrator with deep Terraform and networking expertise.",
        "total_experience_years": 7, "seniority_level": "Senior",
        "job_title": "Cloud Solutions Architect",
        "functional_expertise": [
            {"area": "Cloud & Infrastructure", "details": "Multi-cloud, Terraform, Kubernetes", "years": 7},
            {"area": "DevOps", "details": "CI/CD, infrastructure-as-code", "years": 5},
        ],
        "leadership": {"has_leadership": True, "roles": ["Infrastructure Lead"], "team_size": 5, "responsibilities": ["Cloud strategy", "Cost optimization"]},
        "education": [
            {"degree": "B.Tech", "field": "Electronics", "institution": "NIT Calicut", "graduation_year": 2017}
        ],
        "capability_tags": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "Linux", "Networking", "Python", "CI/CD", "Jenkins", "Git"],
    },
    {
        "name": "Pooja Bhatt", "phone_number": "+91 65567 78899",
        "career_summary": "Data scientist with 5 years of experience in healthcare analytics. Skilled in Python, TensorFlow, and statistical modeling with MLOps experience.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Data Scientist",
        "functional_expertise": [
            {"area": "Data Science", "details": "Statistical modeling, clinical data analysis", "years": 5},
            {"area": "Machine Learning", "details": "ML pipeline design, feature engineering", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Sc", "field": "Computer Science", "institution": "IISc Bangalore", "graduation_year": 2019}
        ],
        "capability_tags": ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Matplotlib", "SQL", "Statistics", "MLOps"],
    },
    {
        "name": "Rohan Verma", "phone_number": "+91 76678 89900",
        "career_summary": "Software engineer with 5 years of experience in full-stack development for SaaS products. Proficient in JavaScript, Python, React, and Node.js.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Software Engineer",
        "functional_expertise": [
            {"area": "Full Stack Development", "details": "React, Node.js, Python, SQL", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Information Technology", "institution": "NIT Jaipur", "graduation_year": 2019}
        ],
        "capability_tags": ["JavaScript", "Python", "Node.js", "TypeScript", "SQL", "React", "Docker", "Git", "REST API", "Algorithm Design"],
    },
    {
        "name": "Nikhil Mehta", "phone_number": "+91 87789 90011",
        "career_summary": "Senior Java developer with 7 years of experience building enterprise microservices for BFSI clients. Strong in Spring Boot, Hibernate, and Kafka.",
        "total_experience_years": 7, "seniority_level": "Senior",
        "job_title": "Senior Java Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Java, Spring Boot, Kafka, distributed systems", "years": 7},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "MCA", "field": "Computer Applications", "institution": "NIT Kurukshetra", "graduation_year": 2017}
        ],
        "capability_tags": ["Java", "Spring", "Hibernate", "Microservices", "Kafka", "MySQL", "REST API", "Docker", "Maven", "Git"],
    },
    {
        "name": "Ananya Joshi", "phone_number": "+91 98890 01122",
        "career_summary": "Python backend developer with 4 years of experience building FastAPI and Django services for fintech applications. Skilled in PostgreSQL, Redis, and Celery.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "FastAPI, Django, PostgreSQL, background jobs", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "VIT Vellore", "graduation_year": 2020}
        ],
        "capability_tags": ["Python", "FastAPI", "Django", "PostgreSQL", "SQLAlchemy", "Docker", "Redis", "Celery", "REST API", "Git", "SQL", "AWS"],
    },
    {
        "name": "Rohit Gupta", "phone_number": "+91 19901 12233",
        "career_summary": "Machine learning engineer with 4 years of experience in recommendation systems and NLP for e-commerce. Strong Python, TensorFlow, and Scikit-learn background.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "ML Engineer",
        "functional_expertise": [
            {"area": "Machine Learning", "details": "Recommendation systems, NLP", "years": 4},
            {"area": "Data Science", "details": "A/B testing, feature engineering", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Tech", "field": "AI & Machine Learning", "institution": "IIT Kharagpur", "graduation_year": 2020}
        ],
        "capability_tags": ["Python", "Pandas", "NumPy", "Machine Learning", "SQL", "Statistics", "Scikit-learn", "Docker", "Git", "AWS"],
    },
    {
        "name": "Ishita Banerjee", "phone_number": "+91 20012 23344",
        "career_summary": "Frontend developer with 4 years of experience building React interfaces for media and e-commerce platforms. Strong in TypeScript, Redux, and CSS architecture.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "Frontend Developer",
        "functional_expertise": [
            {"area": "Frontend Development", "details": "React, Redux, TypeScript, responsive design", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "Jadavpur University", "graduation_year": 2020}
        ],
        "capability_tags": ["JavaScript", "CSS", "HTML", "React", "Redux", "TypeScript", "Jest", "Git", "Webpack"],
    },
    {
        "name": "Sameer Agrawal", "phone_number": "+91 31123 34455",
        "career_summary": "DevOps engineer with 5 years of experience automating CI/CD and infrastructure for SaaS companies. Certified AWS solutions architect with Kubernetes expertise.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "DevOps Engineer",
        "functional_expertise": [
            {"area": "DevOps", "details": "AWS, Docker, Kubernetes, Terraform", "years": 5},
            {"area": "Cloud & Infrastructure", "details": "Multi-account AWS architecture", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.E.", "field": "Electronics", "institution": "Symbiosis Pune", "graduation_year": 2019}
        ],
        "capability_tags": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux", "Jenkins", "Ansible", "Python", "CI/CD", "Bash", "Git"],
    },
    {
        "name": "Nandini Rao", "phone_number": "+91 42234 45566",
        "career_summary": "Junior data analyst with 2 years of experience in retail and logistics analytics. Skilled in SQL, Python, and Tableau with strong visualization skills.",
        "total_experience_years": 2, "seniority_level": "Junior",
        "job_title": "Data Analyst",
        "functional_expertise": [
            {"area": "Data Analytics", "details": "Retail analytics, dashboards", "years": 2},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Sc", "field": "Statistics", "institution": "University of Hyderabad", "graduation_year": 2022}
        ],
        "capability_tags": ["SQL", "Excel", "Python", "Pandas", "Power BI", "Tableau", "Statistics", "Data Visualization"],
    },
    {
        "name": "Pranav Shah", "phone_number": "+91 53345 56677",
        "career_summary": "Backend developer with 3 years of experience building FastAPI and Django services. Familiar with PostgreSQL, Redis, and container-based deployments.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Python Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "FastAPI, Django, PostgreSQL", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "BCA", "field": "Computer Applications", "institution": "Symbiosis Pune", "graduation_year": 2021}
        ],
        "capability_tags": ["Python", "Django", "FastAPI", "PostgreSQL", "MySQL", "Docker", "Redis", "REST API", "Celery", "Git"],
    },
    {
        "name": "Shruti Khanna", "phone_number": "+91 64456 67788",
        "career_summary": "Senior ML engineer with 6 years of experience in NLP, computer vision, and MLOps at media companies. Expert in PyTorch, TensorFlow, and production ML systems.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Senior ML Engineer",
        "functional_expertise": [
            {"area": "Machine Learning", "details": "NLP, Transformers, Computer Vision", "years": 6},
            {"area": "MLOps", "details": "Model serving, A/B testing, monitoring", "years": 3},
        ],
        "leadership": {"has_leadership": True, "roles": ["ML Team Lead"], "team_size": 4, "responsibilities": ["Model architecture decisions", "ML strategy"]},
        "education": [
            {"degree": "M.S.", "field": "Artificial Intelligence", "institution": "Stanford University", "graduation_year": 2018}
        ],
        "capability_tags": ["Python", "PyTorch", "TensorFlow", "NLP", "Transformers", "Computer Vision", "MLOps", "SQL", "Docker", "Git"],
    },
    {
        "name": "Kunal Chawla", "phone_number": "+91 75567 78899",
        "career_summary": "Full-stack developer with 6 years of experience delivering SaaS products. Strong React, Node.js, PostgreSQL, and GraphQL expertise.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Senior Full Stack Developer",
        "functional_expertise": [
            {"area": "Full Stack Development", "details": "React, Node.js, GraphQL, PostgreSQL", "years": 6},
            {"area": "Cloud & Infrastructure", "details": "AWS, Docker", "years": 3},
        ],
        "leadership": {"has_leadership": True, "roles": ["Tech Lead"], "team_size": 5, "responsibilities": ["Architecture", "Sprint planning"]},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "DTU", "graduation_year": 2018}
        ],
        "capability_tags": ["JavaScript", "TypeScript", "React", "Node.js", "PostgreSQL", "MongoDB", "GraphQL", "Docker", "Git", "REST API"],
    },
    {
        "name": "Tanya Gill", "phone_number": "+91 86678 89900",
        "career_summary": "Data analyst with 3 years of experience in financial services. Skilled in Python, SQL, Excel, and Power BI for KPI reporting and risk analysis.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Data Analyst",
        "functional_expertise": [
            {"area": "Data Analytics", "details": "Financial analytics, risk reporting", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Sc", "field": "Statistics", "institution": "Delhi University", "graduation_year": 2021}
        ],
        "capability_tags": ["Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Machine Learning", "Statistics", "Data Visualization", "Excel"],
    },
    {
        "name": "Varun Bhatia", "phone_number": "+91 97789 90011",
        "career_summary": "Java backend developer with 5 years of experience building high-throughput microservices for BFSI clients. Strong in Spring Boot, Kafka, and Redis.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Java Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Java microservices, event-driven systems", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Information Technology", "institution": "Manipal Institute of Technology", "graduation_year": 2019}
        ],
        "capability_tags": ["Java", "Spring Boot", "Microservices", "MySQL", "Redis", "Docker", "Kafka", "REST API", "Git", "Maven"],
    },
    {
        "name": "Divya Menon", "phone_number": "+91 18890 01122",
        "career_summary": "Backend developer with 3 years of experience building Python APIs for edtech. Proficient in FastAPI, Flask, PostgreSQL, and background task processing.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "FastAPI, Flask, PostgreSQL", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Sc", "field": "Computer Science", "institution": "University of Kerala", "graduation_year": 2021}
        ],
        "capability_tags": ["Python", "FastAPI", "Flask", "PostgreSQL", "SQLAlchemy", "Docker", "Redis", "Celery", "REST API", "Git", "SQL"],
    },
    {
        "name": "Rahul Nair", "phone_number": "+91 29901 12233",
        "career_summary": "Senior full-stack developer with 7 years of experience in SaaS platforms. Strong React, Node.js, Python, and AWS background with microservices expertise.",
        "total_experience_years": 7, "seniority_level": "Senior",
        "job_title": "Senior Full Stack Developer",
        "functional_expertise": [
            {"area": "Full Stack Development", "details": "React, Node.js, Python, microservices", "years": 7},
            {"area": "Cloud & Infrastructure", "details": "AWS, ECS, RDS", "years": 4},
        ],
        "leadership": {"has_leadership": True, "roles": ["Tech Lead"], "team_size": 6, "responsibilities": ["Technical mentoring", "Architecture decisions"]},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "NIT Rourkela", "graduation_year": 2017}
        ],
        "capability_tags": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "AWS", "Docker", "SQL", "Git", "REST API"],
    },
    {
        "name": "Neha Sharma", "phone_number": "+91 30012 23344",
        "career_summary": "ML engineer with 4 years of experience in NLP and time-series forecasting. Skilled in PyTorch, Scikit-learn, and building ML pipelines with Docker.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "Machine Learning Engineer",
        "functional_expertise": [
            {"area": "Machine Learning", "details": "NLP, time-series, model deployment", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Tech", "field": "AI & ML", "institution": "IIT Hyderabad", "graduation_year": 2020}
        ],
        "capability_tags": ["Python", "PyTorch", "Scikit-learn", "NLP", "SQL", "Docker", "Git", "Statistics", "Pandas", "NumPy"],
    },
    {
        "name": "Deepak Agarwal", "phone_number": "+91 41123 34455",
        "career_summary": "Senior DevOps engineer with 7 years of experience automating infrastructure on AWS and Kubernetes. Certified Kubernetes administrator with strong monitoring skills.",
        "total_experience_years": 7, "seniority_level": "Lead",
        "job_title": "DevOps Lead",
        "functional_expertise": [
            {"area": "DevOps", "details": "Kubernetes, AWS, Terraform, Jenkins", "years": 7},
            {"area": "Cloud & Infrastructure", "details": "AWS, networking, security", "years": 5},
        ],
        "leadership": {"has_leadership": True, "roles": ["DevOps Lead", "Incident Commander"], "team_size": 6, "responsibilities": ["Platform reliability", "On-call rotations", "Incident response"]},
        "education": [
            {"degree": "B.E.", "field": "Electrical Engineering", "institution": "BIT Mesra", "graduation_year": 2017}
        ],
        "capability_tags": ["Docker", "Kubernetes", "AWS", "Jenkins", "Ansible", "Terraform", "Python", "Linux", "Bash", "CI/CD", "Git", "Prometheus"],
    },
    {
        "name": "Anjali Gupta", "phone_number": "+91 52234 45566",
        "career_summary": "Frontend developer with 3 years of experience building React and TypeScript interfaces for e-commerce. Strong in Redux, Jest, and accessibility.",
        "total_experience_years": 3, "seniority_level": "Mid-Level",
        "job_title": "Frontend Developer",
        "functional_expertise": [
            {"area": "Frontend Development", "details": "React, TypeScript, Redux", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "BCA", "field": "Computer Applications", "institution": "IP University Delhi", "graduation_year": 2021}
        ],
        "capability_tags": ["JavaScript", "HTML", "CSS", "React", "TypeScript", "Redux", "Jest", "Webpack", "Git"],
    },
    {
        "name": "Prakash Joshi", "phone_number": "+91 63345 56677",
        "career_summary": "Senior Java architect with 8 years of experience designing and delivering enterprise microservices for BFSI clients. Expert in Spring Boot, Hibernate, and system design.",
        "total_experience_years": 8, "seniority_level": "Lead",
        "job_title": "Lead Java Architect",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Java, Spring Boot, distributed systems", "years": 8},
            {"area": "System Design", "details": "High-availability, fault-tolerant architecture", "years": 5},
        ],
        "leadership": {"has_leadership": True, "roles": ["Tech Lead", "Architect"], "team_size": 8, "responsibilities": ["System design reviews", "Technical mentoring", "Architecture governance"]},
        "education": [
            {"degree": "MCA", "field": "Computer Applications", "institution": "NIT Surathkal", "graduation_year": 2016}
        ],
        "capability_tags": ["Java", "Spring", "Spring Boot", "Hibernate", "PostgreSQL", "MySQL", "Microservices", "Git", "Maven"],
    },
    {
        "name": "Sneha Verma", "phone_number": "+91 74456 67788",
        "career_summary": "Backend developer with 5 years of experience building Python and FastAPI services for fintech. Strong in PostgreSQL, Redis, and background job orchestration.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Senior Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "FastAPI, PostgreSQL, Kafka, Redis", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "NIT Allahabad", "graduation_year": 2019}
        ],
        "capability_tags": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Redis", "SQL", "Git", "Celery", "Kafka", "AWS"],
    },
    {
        "name": "Manish Verma", "phone_number": "+91 85567 78899",
        "career_summary": "Machine learning engineer with 6 years of experience in computer vision and NLP for media. Expert in PyTorch, TensorFlow, and Kubernetes-based ML infrastructure.",
        "total_experience_years": 6, "seniority_level": "Senior",
        "job_title": "Senior ML Engineer",
        "functional_expertise": [
            {"area": "Machine Learning", "details": "Computer Vision, NLP, Transformers", "years": 6},
            {"area": "DevOps", "details": "Kubernetes, Docker, ML infrastructure", "years": 3},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.Tech", "field": "AI & ML", "institution": "IIT Bombay", "graduation_year": 2018}
        ],
        "capability_tags": ["Python", "TensorFlow", "Keras", "PyTorch", "Scikit-learn", "ML Ops", "Docker", "SQL", "Git", "AWS", "NLP"],
    },
    {
        "name": "Gaurav Sharma", "phone_number": "+91 96678 89900",
        "career_summary": "Business intelligence analyst with 4 years of experience in retail and e-commerce. Skilled in Power BI, Tableau, SQL, and Python for data visualization.",
        "total_experience_years": 4, "seniority_level": "Mid-Level",
        "job_title": "BI Analyst",
        "functional_expertise": [
            {"area": "Data Analytics", "details": "BI dashboards, retail analytics", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Com", "field": "Commerce", "institution": "Delhi University", "graduation_year": 2020}
        ],
        "capability_tags": ["SQL", "Power BI", "Tableau", "Python", "Excel", "Pandas", "Statistics", "Data Visualization", "NumPy"],
    },
    {
        "name": "Kavya Singh", "phone_number": "+91 17789 90011",
        "career_summary": "Junior backend developer with 2 years of experience building Django and Flask APIs for fintech startups. Comfortable with PostgreSQL, Redis, and REST design.",
        "total_experience_years": 2, "seniority_level": "Junior",
        "job_title": "Backend Developer",
        "functional_expertise": [
            {"area": "Backend Development", "details": "Django, Flask, PostgreSQL", "years": 2},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "BCA", "field": "Computer Applications", "institution": "Christ University Bangalore", "graduation_year": 2022}
        ],
        "capability_tags": ["Python", "Django", "Flask", "PostgreSQL", "MySQL", "REST API", "Docker", "Redis", "Celery", "Git", "SQL"],
    },
    {
        "name": "Arjun Nair", "phone_number": "+91 28890 01122",
        "career_summary": "Full-stack developer with 5 years of experience building Angular and Node.js applications for media. Proficient in GraphQL, PostgreSQL, and Docker.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Full Stack Developer",
        "functional_expertise": [
            {"area": "Full Stack Development", "details": "Angular, Node.js, GraphQL", "years": 5},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "B.Tech", "field": "Computer Science", "institution": "NIT Surathkal", "graduation_year": 2019}
        ],
        "capability_tags": ["JavaScript", "TypeScript", "Angular", "Node.js", "PostgreSQL", "GraphQL", "Docker", "Git", "REST API"],
    },
    {
        "name": "Aisha Khan", "phone_number": "+91 39901 12233",
        "career_summary": "Data scientist with 5 years of experience in healthcare and e-commerce. Skilled in Python, SQL, and ML pipelines. Strong in statistical analysis and predictive modeling.",
        "total_experience_years": 5, "seniority_level": "Senior",
        "job_title": "Data Scientist",
        "functional_expertise": [
            {"area": "Data Science", "details": "Predictive modeling, A/B testing", "years": 5},
            {"area": "Machine Learning", "details": "Recommendation systems, classification", "years": 4},
        ],
        "leadership": {"has_leadership": False, "roles": [], "team_size": None, "responsibilities": []},
        "education": [
            {"degree": "M.S.", "field": "Data Science", "institution": "UC Berkeley", "graduation_year": 2019}
        ],
        "capability_tags": ["Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Statistics", "Machine Learning", "Data Visualization", "Docker", "Git"],
    },
]