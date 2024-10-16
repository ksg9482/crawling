from datetime import datetime
import bisect
import requests
import json
import re
import os
from threading import Lock

import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from .constants import job_mapping, skill_mapping


scheduler = None
job_locks = {
    'jobplanet': Lock(),
    'jumpit': Lock()
}

def jobplanet_scheduled_job():
    
    def extract_recruitment_text(data_list, id):
        """
        특정 id를 기준으로 recruitment_text 값을 추출하여 추가
        """
        data_list.sort(key=lambda x: x['id'])
        id_list = [item['id'] for item in data_list]
        index = bisect.bisect_left(id_list, id)
        if index < len(id_list) and id_list[index] == id:
            return data_list[index].get('recruitment_text')
        
        return None

    def minmaxcarrer(recruitment_text):
        """
        경력 범위 추출
        """
        if recruitment_text:
            text = recruitment_text[0]
            if "경력무관" in text:
                min_career = 0
                max_career = 0
            else:
                match = re.search(r'(\d+)\s*~\s*(\d+)', text)
                if match:
                    min_career = int(match.group(1))
                    max_career = int(match.group(2))
                else:
                    min_career = None
                    max_career = None
        return min_career, max_career

    def map_job_title(job_types):
        """
        job type 정규화를 위한 mapping
        """
        return [job_mapping.get(job_type, job_type) for job_type in job_types]

    def determine_carrer(min_career, max_career):
        if min_career == 0:
            if max_career == 0:
                return "경력무관"
            return "신입"
        return "경력"

    def map_skills(skills_list, skills_mapping):
        mapped_skills = []
        for skill in skills_list:
            mapped = False
            for key, values in skills_mapping.items():
                if skill in values:
                    mapped_skills.append(key)
                    mapped = True
                    break
            if not mapped:
                mapped_skills.append(skill)
        return mapped_skills
    
    def param(occupation_level1, occupation_level2 , page):
        # Define the parameters
        params = {
            'occupation_level1': occupation_level1,
            'occupation_level2': occupation_level2,
            'years_of_experience': '',
            'review_score': '',
            'job_type': '',
            'city': '',
            'education_level_id': '',
            'order_by': 'aggressive',
            'page': page,
            'page_size': 10
        }

        return params
    
    def generate_filename(site_name):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_period = 1 if now.hour < 12 else 2  # 오전/오후 구분
        filename = f"{date_str}_{site_name}_{time_period}.json"
        directory_path = './data'
        os.makedirs(directory_path, exist_ok=True)
        return directory_path + '/' + filename
    
    keys_to_extract = ['id', 'title', 'recruitment_text']
    data_list = []
    id_list = []

    headers = {
        'accept': 'application/json',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'jp-os-type': 'web',
        # jps-ssr-auth : 필수
        'jp-ssr-auth': 'jobplanet_desktop_ssr_1d6f8a5f219176accbb8fe051729fc6a',
    }
    # id 추출
    occupation_level1_ids = [(11912, '데이터'), (11600, '개발')]
    for level1_id, _ in occupation_level1_ids:
        occupation_level1 = level1_id
        occupation_level2 = ''
        
        url = "https://www.jobplanet.co.kr/api/v3/job/postings"

        i = 1
        while True:
            print(i)

            params = param(occupation_level1, occupation_level2, i)
            response = requests.get(url, params=params, headers=headers)
            data = response.json()['data']['recruits']
            
            # 데이터가 없으면 반복을 중지
            if len(data) == 0:
                break
            
            id_result = list(map(lambda x: x['id'], data))
            id_list.extend(id_result)
            data_result = list(map(lambda x: {key: x[key] for key in keys_to_extract}, data))
            data_list.extend(data_result)
            
            i += 1

    # 데이터 가공
    total_Processing_result_list = []
    url = "https://www.jobplanet.co.kr/api/v1/job/postings/"

    keys_to_extract = ['name', 'title', 'skills', 'working_area', 'occupations_level1', 'occupations', 'end_at']

    for id in id_list:
        print(id)

        response = requests.get(url + str(id), headers=headers)
        data = response.json()['data']
        
        # Check if the response data is a dictionary
        if isinstance(data, dict):
            result = {key: data.get(key) for key in keys_to_extract}
            recruitment_text = extract_recruitment_text(data_list, id)
            min_career, max_career = minmaxcarrer(recruitment_text)

            result['recruit_id'] = id
            result['company_name'] = result.pop('name')
            result['job_type'] = result.pop('occupations_level1')
            result['sub_types'] = map_job_title(result.pop('occupations'))
            result['skills'] = list(set(map_skills(result.pop('skills'), skill_mapping)))
            result['deadline'] = datetime.strptime(result.pop('end_at'), '%Y.%m.%d').strftime('%Y-%m-%d')
            result['location'] = result.pop('working_area')
            result['career'] = determine_carrer(min_career, max_career)
            result['min_career'] = min_career
            result['max_career'] = max_career
            result['url'] = 'https://www.jobplanet.co.kr/job/search?posting_ids%5B%5D=' + str(id)

            total_Processing_result_list.append(result)

    output_filename = generate_filename("jobplanet")
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(total_Processing_result_list, json_file, ensure_ascii=False, indent=4)


def jumpit_scheduled_job():
    def map_skill(skill):
        skill_lower = skill.lower()  # 입력된 스킬명을 소문자로 변환
        for category, synonyms in skill_mapping.items():
            if skill_lower in [synonym.lower() for synonym in synonyms]:
                return category  # 매핑된 카테고리를 반환
        return skill  # 매핑되지 않으면 원래 스킬 반환

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
        directory_path = './data'
        os.makedirs(directory_path, exist_ok=True)
        return directory_path + '/' + filename

    job_data = []
    page = 1

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
                
                #
                tech_stacks = [map_skill(tech_stack) for tech_stack in position.get('techStacks', [])]
                # 직종 매핑
                sub_types = []
                categories = job_category.split(',')
                for category in categories:
                    sub_types.extend(job_mapping.get(category.strip(), []))
                sub_types = sorted(set(sub_types))
                job_type = determine_job_type(sub_types)
                career = determine_career(min_career, max_career)
                formatted_date = closing_date.split("T")[0] if closing_date != "N/A" else "N/A"
                job_url = f"https://jumpit.saramin.co.kr/position/{job_id}"
                
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


# 크롤링 cron 코드. hour='23', minute='50'이면 매일 23시50분에 실행. 크롤링 시간 필요하므로 텀 두는 것 권장
def start():
    global scheduler
    if not scheduler:
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_job(jumpit_scheduled_job, 'cron', hour='11', minute='30', id='jumpit_am')
        scheduler.add_job(jobplanet_scheduled_job, 'cron', hour='11', minute='35', id='jobplanet_am')
        scheduler.add_job(jumpit_scheduled_job, 'cron', hour='23', minute='30', id='jumpit_pm')
        scheduler.add_job(jobplanet_scheduled_job, 'cron', hour='23', minute='35', id='jobplanet_pm')
        scheduler.start()

        # 앱 종료 시 스케줄러 종료
        atexit.register(lambda: scheduler.shutdown())
