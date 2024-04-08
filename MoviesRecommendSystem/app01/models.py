from django.db import models
from django.db.models import Avg


class Genre(models.Model):
    """电影的类别"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"<Genre:{self.name}>"

    class Meta:
        db_table = 'tb_genre'


class Movie(models.Model):
    """电影的相关信息"""
    # 电影名
    name = models.CharField(max_length=256)
    # imdb_id是info文件里面的电影顺序
    imdb_id = models.IntegerField()
    # 时长
    duration = models.CharField(max_length=256, blank=True)
    # 类型
    genre = models.ManyToManyField(Genre)
    # 发行时间
    release_time = models.CharField(max_length=256, blank=True)
    # 简介
    intro = models.TextField(blank=True)
    # 导演
    director = models.CharField(max_length=256, blank=True)
    # 编剧
    writers = models.CharField(max_length=256, blank=True)
    # 演员
    actors = models.CharField(max_length=512, blank=True)
    # 电影和电影之间的相似度,A和B的相似度与B和A的相似度是一致的，所以symmetrical设置为True
    movie_similarity = models.ManyToManyField("self", through="Movie_similarity", symmetrical=True)
    # 喜爱数
    like_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'tb_movie'

    def __str__(self):
        return f"{self.name},{self.id}"

    def get_score(self):
        # 定义一个获取平均分的方法，模板中直接调用即可
        # 格式 {'score__avg': 3.125}
        result_dct = self.movie_rating_set.aggregate(Avg('score'))
        try:
            # 只保留一位小数
            result = round(result_dct['score__avg'], 1)
        except TypeError:
            return 0
        else:
            return result

    def get_user_score(self, userid):
        return self.movie_rating_set.filter(user=userid).values('score')

    def get_score_int_range(self):
        return range(int(self.get_score()))

    def get_genre(self):
        genre_dct = self.genre.all().values('name')
        genre_lst = []
        for dct in genre_dct.values():
            genre_lst.append(dct['name'])
        return ", ".join(genre_lst)

    def get_similarity(self, k=5):
        # 获取5部最相似的电影的id
        similarity_movies = self.movie_similarity.all()[:k]
        # movies=Movie.objects.filter(=similarity_movies)
        # print(movies)
        return similarity_movies


class UserInfo(models.Model):
    """用户"""
    name = models.CharField(verbose_name='用户名', max_length=64)
    psw = models.CharField(verbose_name='密码', max_length=64)
    email = models.EmailField(unique=True)
    rating_movies = models.ManyToManyField(Movie, through="Movie_rating")
    icon_url = models.CharField(max_length=256)
    # 上次登录时间
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id},{self.name}"

    class Meta:
        db_table = 'tb_userinfo'

    def get_rating_movies(self):
        movie_list = self.rating_movies.all()
        m_list = []
        for i in range(5):
            m_list.append(movie_list[i].name)
        content = ', '.join(m_list)
        if len(movie_list) > 5:
            content = content + " ..."
        return content

    def get_all_ratting(self):
        movie_list = self.rating_movies.all()
        # id_list = [x.id for x in movie_list]
        return movie_list


class Admin(models.Model):
    """管理员"""
    name = models.CharField(verbose_name='管理员名', max_length=16)
    psw = models.CharField(verbose_name='管理员密码', max_length=64)
    # 上次登录时间
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tb_admin'


class Task(models.Model):
    """任务"""
    level_choices = (
        (1, "紧急"),
        (2, "重要"),
        (3, "一般"),
    )
    level = models.SmallIntegerField(verbose_name="级别", choices=level_choices, default=1)
    title = models.CharField(verbose_name="标题", max_length=64)
    detail = models.TextField(verbose_name="详细信息", max_length=128)
    user = models.ForeignKey(verbose_name="负责人", to="Admin", on_delete=models.CASCADE)


class Order(models.Model):
    """订单"""
    oid = models.CharField(verbose_name="订单号", max_length=64)
    title = models.CharField(verbose_name="商品名", max_length=64)
    price = models.IntegerField(verbose_name="价格")
    status_choices = (
        (1, "待支付"),
        (2, "已支付"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    admin = models.ForeignKey(verbose_name="管理员", to="Admin", on_delete=models.CASCADE)


class Movie_similarity(models.Model):
    """电影相似度表"""
    movie_id1 = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False, related_name='similar_movies_1')
    movie_id2 = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False, related_name='similar_movies_2')
    score = models.FloatField(verbose_name="相似度")

    class Meta:
        db_table = 'tb_movie_similarity'


class Movie_rating(models.Model):
    """电影评分"""
    # 评分的用户
    user_id = models.ForeignKey(UserInfo, on_delete=models.CASCADE, unique=False)
    # 评分的电影
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False)
    # 分数
    score = models.FloatField()

    class Meta:
        db_table = 'tb_movie_ratting'

    def __str__(self):
        return f"<Movie_rating: uid:{self.user.id} movie_id:{self.movie.id}>"


class Comment(models.Model):
    """评论表"""
    # 评分的用户
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, unique=False)
    # 评分的电影
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False)
    # 分数
    comment = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = 'tb_comment'

    def __str__(self):
        return f"<Comment: uid:{self.user.id} movie_id:{self.movie.id}>"


class User_rec(models.Model):
    """用户推荐表"""
    # 评分的用户
    user_id = models.ForeignKey(UserInfo, on_delete=models.CASCADE, unique=False)
    # 评分的电影
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False)
    score = models.FloatField(verbose_name="相似度")

    class Meta:
        db_table = 'tb_user_rec'


class Movie_ranking(models.Model):
    """排行榜"""
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, default=1)
    rank = models.IntegerField(default=1)

    class Meta:
        db_table = 'tb_movie_ranking'
