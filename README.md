图片无法正常显示可以查看项目中的版本

1.运行方式：直接运行，代码会读取org_names.json中的公司名从天眼查上请求数据运行，爬到的数据无论（中间是否中断）会存到org_product_datas.json。运行前请先将自己的cookie放在代码header里;

2.Cookie获取方式：
![image](https://github.com/isuco/ImageRository/tree/master/images/cb1.jpg)
 
1)登陆后随便搜索一个公司，在开发者工具中Network中找到图中红线标出的请求链接(search?key=……………………..),
 ![image](https://github.com/isuco/ImageRository/tree/master/images/cb2.png)
2）把Request Headers 中的Cookie信息复制出来。

3.爬取过程中可能会爆出error, 
 ![image](https://github.com/isuco/ImageRository/tree/master/images/cb3.png)
可能是因为如下几种情况：1）触发了反扒机制，大概是50次请求会被怀疑是爬虫，应该是通过IP和cookie中的账号判断的，这时就需要手动去验证一下，然后再次运行。
 ![image](https://github.com/isuco/ImageRository/tree/master/images/cb4.png)
2）出现了爬虫需要但是不能处理的信息结构，这时可以记录下来然后联系李季杰处理。
3）服务器抽风，再次运行即可。


