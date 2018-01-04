import time

# 线程池最大线程数量
max_workers = 10

# 爬虫网站配置
spider_info = {
    'qq': {
        'root': 'http://news.qq.com/',
        'match': "//a[@target='_blank' and "
                 "contains(@href, %s) and "
                 "not(starts-with(text(), '\r\n')) and"
                 "not(starts-with(text(), ' '))]"
                 % time.strftime('%Y%m%d', time.localtime()),
        'attribute': 'href',
    },
    # 'sina': {
    #     'root': 'http://news.sina.com.cn/'
    # }
}



