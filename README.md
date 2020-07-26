# django-mblog 

一款支持多人的博客系统

作为Django学习的入门项目，代码的质量自认为还是有些不足的，可以先去我的博客看一下，喜欢的，求个Star～


个人博客地址：<a href ="https://syzzjw.cn/home_page">syzzjw.cn/home_page</a>


项目部署请参考<a href ="https://syzzjw.cn/notes/user_articles_list/syz_django_deploy/"> Django+nginx+uwsgi+python+celery部署/</a>

## 主要功能：

1.完整的登录，注册，采用celery+邮箱发送验证码登录

2.完整的发表文章,评论文章,回复文章,给文章点赞功能

3.完整的评论,回复，发表，点赞基于websocket通信，基于信号机制，进行全网广播

4.完整的留言板评论，回复，点赞

5.采用whoosh实现全文搜索

6.支持文章标签分类

7.写文章遵循markdown格式，支持代码高亮。

8.自带拉勾网30000+数据分析可视化，以及数据表查询（之前玩爬虫顺手写的，放在了博客上）

9.支持主页文章发表每日记录的热力图可视化和类别词云图（采用Pyecharts)

10.搭配redis实现网站通知和个人文章通知



### 想要互换友链的请留下url～
