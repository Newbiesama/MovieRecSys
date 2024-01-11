"""
自定义分页组件
使用方法：
在视图函数中：
    def user_list(request):
        # 1.根据需求筛选数据
        queryset = models.UserInfo.objects.filter(**data_dict)

        # 2.实例化分页对象
        page_object = Pagination(request, queryset)
        context = {
            'queryset': page_object.page_queryset,  # 搜素结果进行分页
            'page_string': page_object.html(),  # 生成页标的 html
        }
        return render(request, "user_list.html", context)

在 HTML 中：

    {% for obj in queryset %}
        {{ obj.xx }}
    {% endfor %}

    <ul class="pagination">
        {{ page_string }}
    </ul>
"""
import math
import copy

from django.utils.safestring import mark_safe


class Pagination(object):
    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        """
        :param request: 请求的对象
        :param queryset: 符合条件的数据（根据这个数据给他进行分页处理）
        :param page_size: 每页显示多少条数据
        :param page_param: 在URL中传递的获取分页的参数，例如：/?page=12
        :param plus: 显示当前页的前或后几页
        """
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.request = request
        self.query_dict = query_dict
        self.page_param = page_param

        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size
        self.start = (page - 1) * page_size
        self.end = page * page_size
        self.page_queryset = queryset[self.start:self.end]
        self.plus = plus
        # 数据总条数
        self.total_count = queryset.count()
        # 计算页数
        self.page_num = math.ceil(self.total_count / page_size)

    def html(self):
        """生成页标的HTML"""
        # 只显示前后 5 页
        if self.page_num <= 2 * self.plus + 1:
            # 总页数较少，没达到 11 页
            start_page = 1
            end_page = self.page_num
        else:
            # 总页数大于 11 页
            if self.page <= self.plus:
                # 当前页小于 5 时
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                # 当前页大于 5 时
                if (self.page + self.plus) > self.page_num:
                    # 当前页 + 5 大于总页数
                    start_page = self.page_num - 2 * self.plus
                    end_page = self.page_num
                else:
                    # 一般情况
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus
        # 生成页码 html
        page_str_list = []
        # 首页
        self.query_dict.setlist(self.page_param, [1])
        page_str_list.append(f'<li><a href="{self.request.path}?{self.query_dict.urlencode()}">首页</a></li>')
        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
            ele = f'<li><a href="{self.request.path}?{self.query_dict.urlencode()}">上一页</a></li>'
        else:
            self.query_dict.setlist(self.page_param, [1])
            ele = f'<li><a href="{self.request.path}?{self.query_dict.urlencode()}">上一页</a></li>'
        page_str_list.append(ele)
        # 中间页面
        for i in range(start_page, end_page + 1):
            if i == self.page:
                self.query_dict.setlist(self.page_param, [i])
                ele = f'<li class="active"><a href="{self.request.path}?{self.query_dict.urlencode()}">{i:02}</a></li>'
            else:
                self.query_dict.setlist(self.page_param, [i])
                ele = f'<li><a href="{self.request.path}?{self.query_dict.urlencode()}">{i:02}</a></li>'
            page_str_list.append(ele)
        # 下一页
        if self.page < self.page_num:
            self.query_dict.setlist(self.page_param, [self.page + 1])
            ele = f'<li><a href="{self.request.path}?{self.query_dict.urlencode()}">下一页</a></li>'
        else:
            self.query_dict.setlist(self.page_param, [self.page_num])
            ele = f'<li><a href="{self.request.path}?{self.query_dict.urlencode()}">下一页</a></li>'
        page_str_list.append(ele)
        # 尾页
        self.query_dict.setlist(self.page_param, [self.page_num])
        page_str_list.append(f'<li><a href="{self.request.path}?{self.query_dict.urlencode()}">尾页</a></li>')
        # 跳转框
        search_string = """
                <li>
                    <form style="float: left;margin-left: -1px" method="get">
                        <input name="page"
                               style="position: relative;float: left;display: inline-block;width:80px;border-radius: 0;"
                               type="text" class="form-control" placeholder="页码">
                        <button class="btn btn-default" sytle="border-radius: 0" type="submit">跳转</button>
                    </form>
                </li>
            """
        page_str_list.append(search_string)
        page_string = mark_safe("".join(page_str_list))
        return page_string
