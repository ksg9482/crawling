from rest_framework.views import APIView
from rest_framework.response import Response
from .cron import scheduler

class CronJobStatusView(APIView):
    def get(self, request):
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': str(job.next_run_time)
            })
        return Response(jobs)
    