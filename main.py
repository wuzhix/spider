'''
# python3爬虫系统

# 关键字数据表
create table `spider_keyword`
(
    `sk_id` int(10) unsigned not null auto_increment comment '自增id',
    `sk_name` varchar(10) not null default '' comment '关键字名称',
    `sk_add_time` timestamp not null default current_timestamp comment '添加时间',
primary key (`sk_id`),
key `sk_name` (`sk_name`)
)engine=innodb default charset=utf8 comment '关键字数据表';

# 爬虫站点数据表
create table `spider_root`
(
    `sr_id` int(10) unsigned not null auto_increment comment '自增id',
    `sr_url` varchar(256) not null default '' comment '站点url',
    `sr_add_time` timestamp not null default current_timestamp comment '添加时间',
primary key (`sr_id`),
key `sr_url` (`sr_url`(20))
)engine=innodb default charset=utf8 comment '爬虫站点数据表';

# 爬虫网站数据表
create table `spider_web`
(
    `sw_id` int(10) unsigned not null auto_increment comment '自增id',
    `sw_sr_id` int(10) unsigned not null default '0' comment '站点id',
    `sw_title` varchar(256) not null default '' comment '网站标题',
    `sw_url` varchar(256) not null default '' comment '网站url',
    `sw_add_time` timestamp not null default current_timestamp comment '添加时间',
primary key (`sw_id`),
key `sw_sr_id` (`sw_sr_id`),
key `sw_url` (`sw_url`(20))
)engine=innodb default charset=utf8 comment '爬虫网站数据表';

# 关键字映射网站表
create table `spider_keyword_web`
(
    `skw_id` int(10) unsigned not null auto_increment comment '自增id',
    `skw_sk_id` int(10) unsigned not null default '0' comment '关键字id',
    `skw_sw_id` int(10) unsigned not null default '0' comment '网站id',
    `skw_add_time` timestamp not null default current_timestamp comment '添加时间',
primary key (`skw_id`),
key `keyword` (`skw_sk_id`, `skw_add_time`)
)engine=innodb default charset=utf8 comment '关键字映射网站表';
'''

# !/usr/bin/python3
# -*- coding: UTF-8 -*-
import json
from concurrent.futures import ThreadPoolExecutor, wait
import requests
from lxml import html
import conf.settings as conf
import pymysql


def check_web_conf(web_conf):
    '''
    校验web_conf是否有效
    :param web_conf:
    :return:
    '''
    if 'root' not in web_conf.keys():
        return False
    if 'web' not in web_conf.keys():
        return False
    if 'label' not in web_conf['web'].keys():
        return False
    if 'attr' not in web_conf['web'].keys():
        return False
    return True


def get_url_dom(url):
    '''
    根据入口url获取网页dom
    :param url:
    :return:
    '''
    response = requests.get(url)
    if response.status_code == 200:
        # 解析html
        tree = html.fromstring(response.text)
        return tree
    else:
        return None


def get_xpath_dom(tree, xpath):
    '''
    根据xpath，从tree中返回匹配的dom
    :param tree:
    :param xpath:
    :return:
    '''
    dom = tree.xpath(xpath)
    return dom


def get_dom_attr(dom, attr):
    '''
    获取dom的attr属性
    :param dom:
    :param attr:
    :return:
    '''
    return dom.get(attr)


def get_dom_keyword(dom, keyword_conf):
    '''
    根据keyword_conf从dom中提取关键字列表
    :param dom:
    :param keyword_conf:
    :return:
    '''
    if 'label' not in keyword_conf:
        return []
    label = get_xpath_dom(dom, keyword_conf['label'])
    if not label:
        return []
    if 'attr' in keyword_conf:
        keywords = get_dom_attr(label[0], keyword_conf['attr'])
    else:
        keywords = label[0].text
    if 'split' in keyword_conf:
        keyword_list = keywords.split(keyword_conf['split'])
        if 'shield' in keyword_conf:
            keyword_list = [i for i in keyword_list if i not in keyword_conf['shield']]
    else:
        keyword_list = [keywords]
    return keyword_list


def save_data(table, find, insert):
    '''
    保存数据
    :param table:
    :param find:
    :param insert:
    :return:
    '''
    db.ping()
    query_sql = "select * from %s where %s" % (table, find)
    cursor = db.cursor()
    try:
        cursor.execute(query_sql)
        result = cursor.fetchone()
    except:
        print('error: unable to fetch data')
        return None
    if result is None:
        insert_sql = "insert into %s (%s) values (%s)" % (table, insert['key'], insert['value'])
        try:
            cursor.execute(insert_sql)
            db.commit()
        except:
            print('error: unable to insert data')
            db.rollback()
            return None
        try:
            cursor.execute(query_sql)
            res = cursor.fetchone()
        except:
            print('error: unable to fetch data')
            return None
        return res[0]
    else:
        return result[0]


def spider(web_config):
    if check_web_conf(web_config) is False:
        print('param error: ' + json.dumps(web_config, ensure_ascii=False))
        return
    # 解析html
    tree = get_url_dom(web_config['root'])
    if tree is None:
        return
    # 更新到spider_root表
    find = "sr_url='%s'" % web_config['root']
    insert = {'key': 'sr_url', 'value': "'%s'" % web_config['root']}
    root_id = save_data('spider_root', find, insert)
    if root_id is None:
        return
    # 查找网页链接
    doms = get_xpath_dom(tree, web_config['web']['label'])
    for dom in doms:
        url = get_dom_attr(dom, web_config['web']['attr'])
        title = dom.text
        if title is None:
            continue
        web = get_url_dom(url)
        if web is None:
            continue
        find = "sw_url='%s'" % url
        insert = {'key': 'sw_sr_id,sw_title,sw_url', 'value': "%d,'%s','%s'" % (root_id, title, url)}
        web_id = save_data('spider_web', find, insert)
        if web_id is None:
            continue
        print(title, url)
        if 'keyword' in web_config['web'].keys():
            keyword_list = get_dom_keyword(web, web_config['web']['keyword'])
            for keyword in keyword_list:
                if title.find(keyword) == -1 and keyword != '' and len(keyword) < 10:
                    find = "sk_name='%s'" % keyword
                    insert = {'key': 'sk_name', 'value': "'%s'" % keyword}
                    keyword_id = save_data('spider_keyword', find, insert)
                    find1 = "skw_sk_id=%d and skw_sw_id=%d" % (keyword_id, web_id)
                    insert1 = {'key': 'skw_sk_id,skw_sw_id', 'value': "%d,%d" % (keyword_id, web_id)}
                    keyword_web_id = save_data('spider_keyword_web', find1, insert1)


def main():
    # 1、开启线程池
    futures = []
    pool = ThreadPoolExecutor(max_workers=conf.max_workers)
    # 2、遍历爬虫配置
    for web_config in conf.spider_info.values():
        futures.append(pool.submit(spider, web_config))
    # 3、等待爬虫线程全部执行完再退出
    wait(futures)


db = None
if __name__ == '__main__':
    db = pymysql.connect(host=conf.db_host, port=conf.db_port, user=conf.db_user,
                         password=conf.db_pwd, database=conf.db_name, charset='utf8')
    main()
    db.close()
