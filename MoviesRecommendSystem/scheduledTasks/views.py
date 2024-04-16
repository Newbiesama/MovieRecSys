import datetime

from django.contrib import messages
from apscheduler.schedulers.background import BackgroundScheduler
from django.shortcuts import redirect
from django_apscheduler.jobstores import DjangoJobStore

from app01.models import Movie_similarity, UserInfo, User_rec
from app01.utils import data_procession
from app01.utils.recommend import Recommend_Item, Recommend_User


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


def job_rank():
    """计算排行榜定时任务"""
    try:
        data_procession.cal_rank()
        logging.info(f"{datetime.datetime.now()}job_rank is running")
    except Exception as e:
        logging.error(e)


def job_item():
    """计算电影相似度定时任务"""
    try:
        rec = Recommend_Item()
        Movie_similarity.objects.all().delete()
        res = rec.ItemCF_Norm()
        sim_to_create = []
        for mid, ll in res.items():
            for _ in ll:
                sim_to_create.append(Movie_similarity(movie_id1_id=mid, movie_id2_id=list(_)[0], score=list(_)[1]))
        Movie_similarity.objects.bulk_create(sim_to_create)
        logging.info(f"{datetime.datetime.now()}job_item is running")
    except Exception as e:
        logging.error(e)


def job_user():
    """计算用户推荐定时任务"""
    try:
        q_set = UserInfo.objects.all().values_list('id')
        User_rec.objects.all().delete()
        rec_to_create = []
        for uid in q_set:
            uid = uid[0]
            rec = Recommend_User(uid)
            recs = rec.UserIIF()  # [(mid, score), ...]
            for _ in recs:
                rec_to_create.append(User_rec(user_id_id=uid, movie_id_id=_[0], score=_[1]))
        User_rec.objects.bulk_create(rec_to_create)
        logging.info(f"{datetime.datetime.now()}job_user is running")
    except Exception as e:
        logging.error(e)


def set_jobs():
    scheduler.add_job(id='计算排行榜', func=job_rank, trigger='cron', hour=0, minute=0)
    scheduler.add_job(id='计算电影相似度', func=job_item, trigger='cron', hour=1, minute=0)
    scheduler.add_job(id='计算用户推荐结果', func=job_user, trigger='cron', hour=2, minute=0)


# 注：必须得注册到API中去才可以，不然定时任务不能注册，不能执行
def start(request):
    """调度器开始运行"""
    scheduler.start()
    return redirect("/myadmin/")


def init_jobs(request):
    set_jobs()
    return redirect("/myadmin/")


def pause(request):
    # 调度器开始运行
    job_id = request.GET.get('id')
    # print(id)
    # print(print(scheduler.get_job(id).pending))
    scheduler.pause_job(job_id)
    return redirect("/myadmin/")


def stop(request):
    scheduler.shutdown(wait=False)
    return redirect("/myadmin/")


def pause_all(request):
    scheduler.pause()
    return redirect("/myadmin/")


def resume_all(request):
    scheduler.resume()
    return redirect("/myadmin/")


def delete_all(request):
    try:
        scheduler.remove_all_jobs()
        messages.success(request, "删除成功")
    except Exception as e:
        messages.error(request, e)
    return redirect("/myadmin/")
