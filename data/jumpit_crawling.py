import requests
import json
from datetime import datetime
# from mapping import skill_mapping  # map_job.py에서 skill_mapping을 가져옴

# 직종 통일 매핑 사전
job_type_mapping = {
    "서버/백엔드 개발자": ["Back-end Developer"],
    "웹 풀스택 개발자": ["Full-stack Developer", "Back-end Developer", "Front-end Developer"],
    "devops/시스템 엔지니어": ["System Engineer", "Back-end Developer"],
    "프론트엔드 개발자": ["Front-end Developer"],
    "정보보안 담당자": ["Network/Security Engineer"],
    "IOS 개발자": ["Mobile Developer"],
    "안드로이드 개발자": ["Mobile Developer"],
    "QA 엔지니어": ["QA Engineer"],
    "DBA": ["Database Administrator (DBA)"],
    "SW/솔루션": ["Software Developer"],
    "HW/임베디드": ["Embedded Engineer", "Hardware Developer"],
    "블록체인": ["Blockchain Developer"],
    "크로스플랫폼 앱개발자": ["Full-stack Developer", "Mobile Developer"],
    "기술지원": ["Technical Support"],
    "개발 PM": ["Project Manager (PM)"],
    "인공지능/머신러닝": ["AI/ML Engineer"],
    "빅데이터 엔지니어": ["Data Engineer"],
}

skill_mapping = {
    "Cloud-AWS": ["AWS", "aws"],
    "Cloud-AWS S3": ["AWS S3", "Amazon S3"],
    "Cloud-AWS Lambda": ["AWS Lambda"],
    "Cloud-AWS Glue": ["AWS Glue"],
    "Cloud-AWS EC2": ["Amazon EC2", "AWS EC2"],
    "Cloud-AWS Elastic Load Balancing": ["AWS Elastic Load Balancing", "AWS Elastic Load Balancing ..."],
    "Cloud-AWS CodeCommit": ["AWS CodeCommit"],
    "Cloud-AWS Data Pipeline": ["AWS Data Pipeline"],
    "Cloud-AWS IAM": ["AWS IAM"],
    "Cloud-AWS IoT": ["AWS IoT Device Management"],
    "Cloud-AWS Storage Gateway": ["AWS Storage Gateway"],
    "Cloud-AWS X-Ray": ["AWS X-Ray"],
    "Cloud-AWS EKS": ["Amazon EKS"],
    "Cloud-AWS RDS": ["Amazon RDS"],
    "Cloud-GCP": ["GCP", "Google Cloud Platform", "google cloud"],
    "Cloud-GCP BigQuery": ["Google BigQuery"],
    "Cloud-GCP Cloud IoT": ["Google Cloud IoT Core"],
    "Cloud-GCP Load Balancing": ["Google Cloud Load Balancing"],
    "Cloud-GCP Natural Language": ["Google Cloud Natural Language"],
    "Cloud-GCP SQL": ["Google Cloud SQL", "Google Cloud SQL for Postgr..."],
    "Cloud-GCP VPC": ["Google Cloud VPC"],
    "Cloud-Azure": ["Azure", "Microsoft Azure"],
    "Cloud-Azure App Service": ["Azure App Service"],
    "Cloud-Azure IoT": ["Azure IoT Hub"],
    "Cloud-Azure DevOps": ["Azure DevOps", "Azure DevOps Server"],
    "Cloud-Azure Storage": ["Azure Storage"],
    "Cloud-Azure Synapse": ["Azure Synapse"],
    "Cloud-Azure CDN": ["Azure CDN"],
    "Cloud-Azure Application Insights": ["Azure Application Insights"],
    "Languages-Python": ["Python", "python3", "파이썬", "python"],
    "Languages-Java": ["Java", "java", "Java 8", "java ee"],
    "Languages-C#": ["C#", "c#", ".NET", ".NET Core", ".net"],
    "Languages-C++": ["C++", "c++", "C++ Builder", "Visual C++"],
    "Languages-TypeScript": ["TypeScript", "typescript"],
    "Languages-PHP": ["PHP", "php"],
    "Languages-Kotlin": ["Kotlin"],
    "Languages-R": ["R", "r", "R Language"],
    "Languages-Ruby": ["Ruby", "ruby on rails"],
    "Languages-Swift": ["Swift", "swiftui"],
    "Languages-Dart": ["Dart"],
    "Languages-SQL": ["SQL"],
    "Languages-C": ["C"],
    "Languages-Go": ["Golang","Go" ],
    "Web Frameworks-Django": ["Django", "Django REST framework", "Django framework"],
    "Web Frameworks-Flask": ["Flask"],
    "Web Frameworks-Spring": ["Spring", "Spring Boot", "Spring Framework", "Spring Data JPA"],
    "Web Frameworks-React": ["React", "React.js", "React Native", "React Native Seed", "React Navigation", "React Query", "React Redux", "React Router", "React Server", "React.js Boilerplate", "ReactPHP"],
    "Web Frameworks-ExpressJS": ["ExpressJS", "Express"],
    "Web Frameworks-Vue.js": ["Vue.js", "VueJs", "Vue3", "Vuex"],
    "Web Frameworks-AngularJS": ["AngularJS", "Angular 2", "Angular"],
    "DevOps-Docker": ["Docker", "Docker Compose", "Dockerized"],
    "DevOps-Kubernetes": ["Kubernetes", "K8S"],
    "DevOps-Jenkins": ["Jenkins"],
    "DevOps-Terraform": ["Terraform"],
    "DevOps-Ansible": ["Ansible"],
    "DevOps-CircleCI": ["CircleCI"],
    "DevOps-AWS CodePipeline": ["AWS CodePipeline"],
    "DevOps-Git": ["GitHub Actions","git"],
    "Data Science-TensorFlow": ["TensorFlow"],
    "Data Science-PyTorch": ["PyTorch"],
    "Data Science-Pandas": ["Pandas"],
    "Data Science-NumPy": ["NumPy"],
    "Data Science-Scikit-learn": ["scikit-learn"],
    "Data Science-Keras": ["Keras"],
    "Database-MySQL": ["MySQL", "mysql", "MySQL WorkBench"],
    "Database-PostgreSQL": ["PostgreSQL", "postgresql", "PostGIS"],
    "Database-MongoDB": ["MongoDB", "Mongoose"],
    "Database-Redis": ["Redis", "redis"],
    "Database-Cassandra": ["Cassandra"],
    "Database-MSSQL": ["MSSQL", "Microsoft SQL Server", "sql server"],
    "Database-Oracle": ["Oracle", "Oracle PL/SQL", "Oracle DB", "Oracle Integration Cloud"],
    "Database-SQLite": ["SQLite", "SQLAlchemy"],
    "Database-Elasticsearch": ["Elasticsearch"],
    "Mobile Development-Android": ["Android SDK", "Android OS", "android studio"],
    "Mobile Development-iOS": ["iOS", "ios", "iOS 개발"],
    "Mobile Development-Flutter": ["Flutter"],
    "Mobile Development-React Native": ["React Native"],
    "Networking-Firewall": ["Firewall"],
    "Networking-VPN": ["VPN"],
    "Networking-Cisco": ["Cisco", "Cisco ISE"],
    "Networking-TCP/IP": ["TCP/IP", "tcpip"],
    "Containerization-Docker": ["Docker"],
    "Containerization-Kubernetes": ["Kubernetes", "K8S"],
    "Tools-Figma": ["Figma"],
    "Tools-Photoshop": ["Adobe Photoshop"],
    "Tools-Jira": ["Jira"],
    "Tools-Confluence": ["Confluence"],
    "Tools-Slack": ["Slack"],
    "Tools-Sketch": ["Sketch"],
    "Tools-Trello": ["Trello"],
    "Frontend-HTML": ["HTML5", "HTML", "html5"],
    "Frontend-CSS": ["CSS3", "CSS 3", "css"],
    "Frontend-JavaScript": ["JavaScript", "javascript"],
    "Frontend-Sass": ["Sass"],
    "Frontend-Bootstrap": ["Bootstrap"],
    "AI-Deep Learning": ["Deep Learning", "딥러닝", "DeepLearning"],
    "AI-Machine Learning": ["Machine Learning", "머신러닝", "AI", "AI/인공지능", "MachineLearning"],
    "AI-NLP": ["NLP", "자연어처리"],
    "Blockchain-Solidity": ["Solidity"],
    "Blockchain-Hyperledger": ["Hyperledger Fabric", "Hyperledger Indy"],
    "Blockchain-Ethereum": ["Ethereum", "etherscan"],
    "Version Control-Git": ["Git", "GitHub", "GitHub Actions", "GitLab", "Bitbucket", "Git Flow"],
    "Other-Spring Framework": ["Spring", "Spring Boot"],
    "Other-REST API": ["REST API", "RESTful", "rest api", "restful api"],
    "Other-Socket": ["Socket.IO", "SocketCluster"],
    "Other-GraphQL": ["GraphQL"],
    "Other-Prometheus": ["Prometheus"],
    "Other-Kafka": ["Kafka"],
    "Other-Redis": ["Redis", "redis cloud"],
    "Other-OpenAPI": ["OpenAPI"],
    "Other-Swift": ["Swift", "SwiftUI"],
    "Other-Linux": ["Linux", "Ubuntu", "CentOS", "LINUX", "리눅스", "linux-kernel","Embedded Linux"],
    "Other-Windows": ["Windows Server", "Windows","windows", 'window'],
    "Web Frameworks-Next.js": ["Next.js", "next js", "NextJS", "next.js","Nuxt.js"],
    "Web Frameworks-Nest.js": ["nest js", "nest.js", "Nest js", "NestJS"],
    "Web Frameworks-Node.js": ["node.js", "node js", "Node.js", "NodeJS"],
    "Web Frameworks-ASP.NET": ["ASP.NET", "ASP.NET Core", "ASP.NET MVC", ".net"],
    "Tools-Slack": ["Slack", "SLACK", "slack", "슬랙"],
    "Tools-Notion": ["Notion", "노션", "notion"],
    "Web Frameworks-ASP.NET": ["ASP.NET", "ASP.NET Core", "ASP.NET MVC", ".net"],
    "Other-Airflow": ["Airflow", "Apache Airflow", "airflow", "apache airflow"],
    "Other-Spark": ["spark", "Apache Spark", "Spark", "SPARK"],
    "Database-MariaDB": ["MariaDB", "MARIADB", "mariadb", "mariaDB", "Mariadb"],
}
def map_skill(skill):
    skill_lower = skill.lower()  # 입력된 스킬명을 소문자로 변환
    for category, synonyms in skill_mapping.items():
        if skill_lower in [synonym.lower() for synonym in synonyms]:
            return category  # 매핑된 카테고리를 반환
    return skill  # 매핑되지 않으면 원래 스킬 반환

job_data = []
page = 1

# min_career가 0인데 (신입) max_career가 7년 이상이면 경력무관 처리
def determine_career(min_career, max_career):
    if min_career == 0:
        if max_career >= 7:
            return "경력무관"
        return "신입"
    return "경력"

# 직종 결정 함수
def determine_job_type(sub_types):
    data_related_types = ["DBA", "Data Engineer", "AI/ML Engineer"]
    for sub_type in sub_types:
        if sub_type in data_related_types:
            return "데이터"
    return "개발"

# 파일 이름 생성
def generate_filename():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_period = 1 if now.hour < 12 else 2  # 오전/오후 구분
    filename = f"{date_str}_jumpit_{time_period}.json"
    return filename

while True:
    # Jumpit API URL
    url = f"https://jumpit-api.saramin.co.kr/api/positions?sort=rsp_rate&highlight=false&page={page}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if not data['result']['positions']:
            print(f" {page} End")
            break
        
        # 각 'positions' 데이터를 추출
        for position in data['result']['positions']:
            job_id = position.get('id', 'N/A')
            company_name = position.get('companyName', 'N/A')
            title = position.get('title', 'N/A')
            job_category = position.get('jobCategory', 'N/A')
            min_career = position.get('minCareer', 'N/A')
            max_career = position.get('maxCareer', 'N/A')

            location = position.get('locations')[0].split()[0] if position.get('locations') else 'N/A'
            closing_date = position.get('closedAt', 'N/A')
            
            # 기술 스택을 매핑
            tech_stacks = [map_skill(tech_stack) for tech_stack in position.get('techStacks', [])]
            
            job_url = f"https://jumpit.saramin.co.kr/position/{job_id}"
            
            # 직종 매핑
            sub_types = []
            categories = job_category.split(',')
            for category in categories:
                sub_types.extend(job_type_mapping.get(category.strip(), []))
            sub_types = sorted(set(sub_types))
            
            job_type = determine_job_type(sub_types)
            career = determine_career(min_career, max_career)
            
            formatted_date = closing_date.split("T")[0] if closing_date != "N/A" else "N/A"
            
            # 추출한 데이터를 리스트에 추가
            job_data.append({
                'recruit_id': job_id,
                'company_name': company_name,
                'job_type': job_type,
                'sub_types': sub_types,
                'title': title,
                'career': career,
                'min_career': min_career,
                'max_career': max_career,
                'location': [location],
                'skills': tech_stacks,  # 매핑된 스킬 추가
                'deadline': formatted_date,
                'url': job_url
            })
        
        page += 1
    
    else:
        print(f"Error {response.status_code} at page {page}")
        break

# 파일 이름 생성 및 JSON 파일로 저장
output_filename = generate_filename()
with open(output_filename, 'w', encoding='utf-8') as json_file:
    json.dump(job_data, json_file, ensure_ascii=False, indent=4)

print(f"{output_filename} success")