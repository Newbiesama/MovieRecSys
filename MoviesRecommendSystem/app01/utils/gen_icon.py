import os.path

from identicons import generate
from identicons import save


def gen_icon(text):
    """生成头像"""
    try:
        icon = generate(str(text))
        static_url = '/Volumes/HY/PythonProjects/MoviesRecommendSystem/MoviesRecommendSystem/app01/static'
        fn = os.path.join(static_url, 'icons', f"icon_{str(text).replace(' ', '_')}.png")
        save(icon, fn, 500, 500)
        return True
    except Exception as e:
        return e


if __name__ == '__main__':
    gen_icon("dfs")
