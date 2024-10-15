import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

scheduler = None

def jobplanet_scheduled_job():
    # 잡플래닛 크롤링 코드
    print("jobplanet job")

def jumpit_scheduled_job():
    # 점핏 크롤링 코드
    print("jumpit job")


# 크롤링 cron 코드. hour='23', minute='50'이면 매일 23시50분에 실행. 크롤링 시간 필요하므로 텀 두는 것 권장
def start():
    global scheduler
    if not scheduler:
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        # 
        scheduler.add_job(jobplanet_scheduled_job, 'cron', hour='14', minute='00', id='jobplanet')
        scheduler.add_job(jumpit_scheduled_job, 'cron', hour='14', minute='01', id='jumpit')
        scheduler.start()

        # 앱 종료 시 스케줄러 종료
        atexit.register(lambda: scheduler.shutdown())