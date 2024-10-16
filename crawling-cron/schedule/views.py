from threading import Thread
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .cron import scheduler, jobplanet_scheduled_job, jumpit_scheduled_job, job_locks

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


class CronJobExecuteView(APIView):
    def post(self, request, site):
        if site not in ['jobplanet', 'jumpit']:
            return Response({"error": "Invalid site"}, status=status.HTTP_400_BAD_REQUEST)

        job_lock = job_locks[site]
        if not job_lock.acquire(blocking=False):
            return Response({"message": f"{site} crawling is already in progress"}, status=status.HTTP_409_CONFLICT)

        try:
            if site == 'jobplanet':
                Thread(target=self._run_jobplanet_job, args=(job_lock,)).start()
            elif site == 'jumpit':
                Thread(target=self._run_jumpit_job, args=(job_lock,)).start()

            return Response({"message": f"{site} crawling started"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            job_lock.release()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _run_jobplanet_job(self, lock):
        try:
            jobplanet_scheduled_job()
        finally:
            lock.release()

    def _run_jumpit_job(self, lock):
        try:
            jumpit_scheduled_job()
        finally:
            lock.release()