import time

# 线程池最大线程数量
max_workers = 10

# mysql配置
db_name = 'test'
db_host = '127.0.0.1'
db_port = 3306
db_user = 'root'
db_pwd = ''

# 爬虫网站配置
spider_info = {
    'qq': {
        # 爬虫入口
        'root': 'http://news.qq.com/',
        # 抓取网站配置
        'web': {
            # 抓取href属性包含当天日期%Y%m%d格式，文本内容不是' '也不是'\r\n'开头的，在新窗口打开的a标签
            'label': "//a[@target='_blank' and "
                     "contains(@href, %s) and "
                     "not(starts-with(text(), '\r\n')) and"
                     "not(starts-with(text(), ' '))]"
                     % time.strftime('%Y%m%d', time.localtime()),
            # 超链接从标签的href属性获取
            'attr': 'href',
            # 抓取关键字配置
            'keyword': {
                # 抓取name属性为keywords的meta标签
                'label': "//meta[@name='keywords']",
                # 关键字从标签的content属性获取
                'attr': 'content',
                # 关键字分割符
                'split': ','
            }
        }
    }
}



