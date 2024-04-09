import math
import re
import datetime

from app01 import models


def cal_rank():
    """计算排行榜"""
    like_dict = dict()
    try:
        # 获取表数据
        res = models.Movie_rating.objects.all()
        # 计算喜爱数
        for r in res:
            like_dict.setdefault(r.movie_id_id, 0)
            if math.floor(r.score) >= 3:
                like_dict[r.movie_id_id] += 1
        # 更新分数
        for key in like_dict:
            models.Movie.objects.filter(id=int(key)).update(like_count=like_dict[key])
        # 获取发行年份
        pattern = r'\d{4}'
        now_year = datetime.datetime.now().year
        interval_dict = dict()
        for m in models.Movie.objects.all():
            match = re.search(pattern, str(m.release_time))
            if match:
                date_str = match.group()
            else:
                date_str = '1995'
            _interval = now_year - int(date_str)
            interval_dict[m.id] = _interval
        # 计算rank_score
        score_dict = dict()
        for k in like_dict.keys():
            score_dict[k] = like_dict[k] / (interval_dict[k] + 1)
        # 写入 Movie_ranking 表
        models.Movie_ranking.objects.all().delete()
        rank_to_create = []
        for mid, sc in score_dict.items():
            rank_to_create.append(models.Movie_ranking(movie_id_id=mid, rank_score=sc))
        models.Movie_ranking.objects.bulk_create(rank_to_create)
        return True
    except Exception as e:
        # 发生异常时进行处理
        # 可以记录日志、回滚事务等操作
        raise Exception("计算排行榜时发生异常: " + str(e))
