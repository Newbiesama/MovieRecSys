import time


def timer(func):
    """计时器的装饰器"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        stop_time = time.time()
        print(f'Func {func.__name__}, run time: {stop_time - start_time}')
        return res

    return wrapper
