# xhs-spider


小红书博主信息、笔记信息爬虫（写给雪绒）
—— kuloud 2022/1/20

Example:

1. 自行抓包小红书小程序，找用户token，替换{$authorizations}（其实1个就够了，但是小红书访刷做了很多限制，请求频次10s一次基本够用）
2. 需要定期爬的链接列表，自行替换{$URL}
3. 运行脚本，在当前目录生成对应的csv数据

    $ python3 xhs.py

