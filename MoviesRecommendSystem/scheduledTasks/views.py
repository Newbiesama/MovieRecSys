from django.http import HttpResponse
import time
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events

import logging

logging.basicConfig(format='%(asctime)s %(message)s', filename='./logs/scheduledTasks.log', filemode='a+',
                    level=logging.DEBUG)
logging.info('logging started.')

# 关闭django-apscheduler的日志输出
logging.getLogger('apscheduler').setLevel(logging.WARNING)

# 实例化调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
# 调度器使用DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), "default")


# 1.通过 @register_job 类装饰器做法 每间隔5s执行一次
@register_job(scheduler, "interval", seconds=5, args=['job1name'], id='job1', replace_existing=True)
def job1(name):
    # 具体要执行的代码
    logging.info('Job 1 started.')
    # print('{} 任务运行成功！{}'.format(name, time.strftime("%Y-%m-%d %H:%M:%S")))


def job2(name):
    # 具体要执行的代码
    logging.info('Job 2 started.')
    # print('{} 任务运行成功！{}'.format(name, time.strftime("%Y-%m-%d %H:%M:%S")))


# 2.add_job的方式 interval 每间隔10s执行一次
# scheduler.add_job(job2, "interval", seconds=10, args=['job2name'], id="job2", replace_existing=True)

# 调度器开始运行
scheduler.start()


# 注：必须得注册到API中去才可以，不然定时任务不能注册，不能执行
def testTimedTasks(request):
    return HttpResponse('ok')
