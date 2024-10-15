import requests
import json
from datetime import datetime

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

job_data = []
page = 1

# min_career가 0인데 (신입) max_career가 7년 이상이면 그냥 경력무관 뽑기
def determine_career(min_career, max_career):
    if min_career == 0:
        if max_career >= 7:
            return "경력무관"
        return "신입"
    return "경력"

#임시로 해둔건데 직종 추가 시 코드 개선 필요..
def determine_job_type(sub_types):
    data_related_types = ["DBA", "Data Engineer", "AI/ML Engineer"]
    for sub_type in sub_types:
        if sub_type in data_related_types:
            return "데이터"
    return "개발"

while True:
    # Jumpit API URL
    url = f"https://jumpit-api.saramin.co.kr/api/positions?sort=rsp_rate&highlight=false&page={page}"
    
    response = requests.get(url)
    
    # 응답 상태 200 안나오면 status code 반환
    if response.status_code == 200:
        # JSON 데이터 파싱
        data = response.json()
        
        # 더이상 데이터가 없으면 종료메시지
        if not data['result']['positions']:
            print(f" {page} End")
            break
        
        # 각 'positions' 데이터를 추출
        for position in data['result']['positions']:
            job_id = position.get('id', 'N/A') #공고 id
            company_name = position.get('companyName', 'N/A') #기업명
            title = position.get('title', 'N/A') #공고제목
            job_category = position.get('jobCategory', 'N/A') # 플랫폼 통일한 직무 매핑사전으로 후처리 해줄거 
            min_career = position.get('minCareer', 'N/A') # 최소 경력 0이면 신입
            max_career = position.get('maxCareer', 'N/A')

            # location을 바로 슬라이싱하여 시/도까지만 반환
            location = position.get('locations')[0].split()[0] if position.get('locations') else 'N/A'
            
            closing_date = position.get('closedAt', 'N/A')
            
            # 기술 스택을 리스트로 저장
            tech_stacks = [tech_stack for tech_stack in position.get('techStacks', [])]
            
            # URL 생성 (공고 ID를 포함)
            job_url = f"https://jumpit.saramin.co.kr/position/{job_id}"
            
            # 직종 매핑 처리 및 중복 제거
            sub_types = []
            categories = job_category.split(',')
            for category in categories:
                sub_types.extend(job_type_mapping.get(category.strip(), []))
            sub_types = sorted(set(sub_types))
            

            # 임시로 해놓은 job_type 결정 (개발/데이터)
            job_type = determine_job_type(sub_types)
            
            career = determine_career(min_career, max_career)
            
            # 날짜 포맷 변경 2024-12-31T23:59:59 나오던거 T 후 날려버림
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
                'location': location,
                'skills': tech_stacks,
                'deadline': formatted_date,
                'URL': job_url
            })
        
        # 페이지 번호 증가
        page += 1
    
    else:
        print(f"Error {response.status_code} at page {page}")
        break

# JSON 파일로 저장
with open('jumpit_final.json', 'w', encoding='utf-8') as json_file:
    json.dump(job_data, json_file, ensure_ascii=False, indent=4)

print("성공")
