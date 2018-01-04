'''
python3爬虫系统
'''

from concurrent.futures import ThreadPoolExecutor, wait
import requests
from lxml import html
import conf.settings as conf


def spider(web_config):
    # 2、请求页面
    response = requests.get(web_config['root'])
    # 解析html
    tree = html.fromstring(response.text)
    # 查找网页链接
    doms = tree.xpath(web_config['match'])
    for dom in doms:
        url = dom.get(web_config['attribute'])
        title = dom.text


def main():
    # 1、开启线程池
    futures = []
    pool = ThreadPoolExecutor(max_workers=conf.max_workers)
    # 2、遍历爬虫配置
    for web_config in conf.spider_info.values():
        futures.append(pool.submit(spider, web_config))
    # 3、等待爬虫线程全部执行完再退出
    wait(futures)


if __name__ == '__main__':
    main()
