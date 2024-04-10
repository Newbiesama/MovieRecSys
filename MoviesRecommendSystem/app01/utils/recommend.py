import math

from django.db.models import Max
from django.db.models import Subquery
from app01.models import UserInfo, Movie_rating, Movie
from app01.utils.timer import timer


class Recommend_User(object):
    """基于用户的协同过滤算法"""

    def __init__(self, uid):
        """
        初始化参数
        :param uid: 当前用户的id
        """
        # 寻找相似用户的个数
        self.K = 20
        # 推荐电影数量
        self.N = 10
        # 存放当前用户评分过的电影querySet
        self.user_rated_movies = None
        # item-user倒排表
        self.movie_user = self.build_movie_user()
        # 用户id
        self.uid = uid

    @timer
    def build_movie_user(self):
        """构建倒排表"""
        # 是字典，格式: {movie1:{user1, user2, ...}, ...}
        temp = dict()
        # 所有电影
        movie_id_qs = Movie.objects.all().values_list("id", flat=True)
        for movie_id in movie_id_qs:
            rated_user_id = Movie_rating.objects.filter(movie_id=movie_id).values_list("user_id", flat=True)
            for uid in rated_user_id:
                temp.setdefault(movie_id, list())
                temp[movie_id].append(uid)
        return temp

    @timer
    def UserCF(self):
        """基于用户余弦相似度的推荐"""
        # 其他用户与当前用户相似度
        user_sim_dct = dict()
        # 各个用户评分过的电影的数量，即集合的大小
        movie_num_dct = dict()
        # 获取当前用户评分过的电影id
        self.user_rated_movies = Movie_rating.objects.filter(user_id=self.uid).values_list("movie_id", flat=True)
        # 遍历倒排表
        for movie in self.movie_user:
            # 评价该电影的用户列表
            users = self.movie_user[movie]
            # 遍历列表中的用户
            for i in range(len(users)):
                uid = users[i]
                # 记录评价电影的数量
                movie_num_dct.setdefault(uid, 0)
                movie_num_dct[uid] += 1
                # 计算当前用户与其他用户评分过的电影交集数
                if movie in self.user_rated_movies and uid != self.uid:
                    user_sim_dct.setdefault(uid, 0)
                    user_sim_dct[uid] += 1
        # 计算余弦相似度
        cur_user_num = len(self.user_rated_movies)
        for u in user_sim_dct:
            user_sim_dct[u] /= math.sqrt(cur_user_num * movie_num_dct[u])
        # 按照相似度排序
        sorted_user_list = sorted(user_sim_dct.items(), key=lambda x: -x[1])[:self.K]
        # 获取推荐的N部电影
        movies_t = dict()
        for u, _ in sorted_user_list:
            tt = Movie_rating.objects.filter(user_id=u).values_list("movie_id", flat=True)
            for m in tt:
                if m not in self.user_rated_movies:
                    if m not in movies_t:
                        movies_t[m] = 0
                    # 加的是相似度，公式中是 wr，r 都是1，因为这里的用户都是评过分的
                    movies_t[m] += user_sim_dct[u]
        # 格式：[(movie_id, score), (...), ...]
        recs = list(sorted(movies_t.items(), key=lambda x: -x[1]))[:self.N]
        return recs

    @timer
    def UserIIF(self):
        """基于改进的用户相似度算法的推荐"""
        # 其他用户与当前用户相似度
        user_sim_dct = dict()
        # 各个用户评分过的电影的数量，即集合的大小
        movie_num_dct = dict()
        # 获取当前用户评分过的电影id
        self.user_rated_movies = Movie_rating.objects.filter(user_id=self.uid).values_list("movie_id", flat=True)
        # 遍历倒排表
        for movie in self.movie_user:
            # 评价该电影的用户列表
            users = self.movie_user[movie]
            # 遍历列表中的用户
            for i in range(len(users)):
                uid = users[i]
                movie_num_dct.setdefault(uid, 0)
                movie_num_dct[uid] += 1
                # 计算当前用户与其他用户评分过的电影交集数
                if movie in self.user_rated_movies and uid != self.uid:
                    user_sim_dct.setdefault(uid, 0)
                    # 相比UserCF，主要是改进了这里
                    user_sim_dct[uid] += 1 / math.log(1 + len(users))
        # 计算相似度
        cur_user_num = len(self.user_rated_movies)
        for u in user_sim_dct:
            user_sim_dct[u] /= math.sqrt(cur_user_num * movie_num_dct[u])
        # 按照相似度排序
        sorted_user_list = sorted(user_sim_dct.items(), key=lambda x: -x[1])[:self.K]
        # 获取推荐的N部电影
        movies_t = dict()
        for u, _ in sorted_user_list:
            tt = Movie_rating.objects.filter(user_id=u).values_list("movie_id", flat=True)
            for m in tt:
                if m not in self.user_rated_movies:
                    if m not in movies_t:
                        movies_t[m] = 0
                    movies_t[m] += user_sim_dct[u]
        recs = list(sorted(movies_t.items(), key=lambda x: -x[1]))[:self.N]
        return recs


class Recommend_Item(object):
    """基于物品的协同过滤算法"""

    def __init__(self):
        """初始化参数"""
        # 寻找相似物品数目
        self.K = 10
        # 推荐电影数量
        self.N = 10
        # user_item表
        self.user_movie = self.build_user_movie()

    @staticmethod
    @timer
    def build_user_movie():
        """构建user_item表"""
        # 格式: {uid: <QuerySet [...]>, ...}
        # key 是用户 id，value 是该用户评分过的电影 id
        temp = dict()
        user_id_qs = UserInfo.objects.all().values_list("id", flat=True)
        for uid in user_id_qs:
            temp.setdefault(uid, Movie_rating.objects.filter(user_id=uid).values_list("movie_id", flat=True))
        return temp

    @timer
    def ItemCF(self):
        """ItemCF"""
        # 计算物品相似度矩阵
        sim = {}
        num = {}
        for user in self.user_movie:
            movies = self.user_movie[user]
            for i in range(len(movies)):
                m = movies[i]
                if m not in num:
                    num[m] = 0
                num[m] += 1
                if m not in sim:
                    sim[m] = {}
                for j in range(len(movies)):
                    if j == i:
                        continue
                    v = movies[j]
                    if v not in sim[m]:
                        sim[m][v] = 0
                    sim[m][v] += 1
        for m in sim:
            for v in sim[m]:
                sim[m][v] /= math.sqrt(num[m] * num[v])
        # 按照相似度排序
        sorted_item_sim = {k: list(sorted(v.items(), key=lambda x: -x[1])[:5]) for k, v in sim.items()}
        return sorted_item_sim

    @timer
    def ItemIUF(self):
        """基于改进的物品余弦相似度的推荐"""
        # 计算物品相似度矩阵
        sim = {}
        num = {}
        for user in self.user_movie:
            movies = self.user_movie[user]
            for i in range(len(movies)):
                m = movies[i]
                if m not in num:
                    num[m] = 0
                num[m] += 1
                if m not in sim:
                    sim[m] = {}
                for j in range(len(movies)):
                    if j == i:
                        continue
                    v = movies[j]
                    if v not in sim[m]:
                        sim[m][v] = 0
                    sim[m][v] += 1 / math.log(1 + len(movies))
        for m in sim:
            for v in sim[m]:
                sim[m][v] /= math.sqrt(num[m] * num[v])
        # 按照相似度排序
        sorted_item_sim = {k: list(sorted(v.items(), key=lambda x: -x[1])[:5]) for k, v in sim.items()}
        return sorted_item_sim

    @timer
    def ItemCF_Norm(self):
        """基于归一化的物品余弦相似度的推荐"""
        # 计算物品之间的相似度需要知道各自评分的人数，和共同为之评分的人数
        sim = {}
        # num 用来统计每部电影被多少人评了分
        num = {}
        for user in self.user_movie:
            movies = self.user_movie[user]
            for i in range(len(movies)):
                m = movies[i]
                if m not in num:
                    num[m] = 0
                num[m] += 1

                if m not in sim:
                    sim[m] = {}
                for j in range(len(movies)):
                    if j == i:
                        continue
                    v = movies[j]
                    if v not in sim[m]:
                        sim[m][v] = 0
                    sim[m][v] += 1
        for m in sim:
            for v in sim[m]:
                sim[m][v] /= math.sqrt(num[m] * num[v])

        # 对相似度矩阵进行按行归一化
        for u in sim:
            s = 0
            for v in sim[u]:
                s += sim[u][v]
            if s > 0:
                for v in sim[u]:
                    sim[u][v] /= s
        # 按照相似度排序
        sorted_item_sim = {k: list(sorted(v.items(), key=lambda x: -x[1])[:5]) for k, v in sim.items()}
        return sorted_item_sim
