'''
python3爬虫系统
'''

import json
from concurrent.futures import ThreadPoolExecutor, wait
import os


def spider(path_name):
    # 1、读取网站json配置
    with open(path_name, 'r') as f:
        web_config = json.load(f)


def main():
    # 1、从配置文件读取配置信息
    with open('main.json', 'r') as f:
        main_config = json.load(f)
        # print(main_config)
    # 2、开启线程池
    futures = []
    pool = ThreadPoolExecutor(max_workers=main_config['max_workers'])
    # 3、遍历配置目录，启动爬虫方法
    names = os.listdir(main_config['spider_conf'])
    for name in names:
        path_name = main_config['spider_conf'] + '/' + name
        # 如果是json文件，启动线程进行爬虫
        if os.path.isfile(path_name) and os.path.splitext(path_name)[1] == '.json':
            futures.append(pool.submit(spider, path_name))
    # 等待爬虫线程全部执行完再退出
    wait(futures)


if __name__ == '__main__':
    main()
