youku-lixian
=============
优酷视频下载的Python脚本。顺便支持其他……

简介
----
从优酷网站上下载flv或mp4格式的视频文件（包括分段视频的拼接）。友情支持bilibili，acfun，新浪，酷6，pptv，爱奇艺，土豆，搜狐，56，cntv，yinyuetai，凤凰网。
除Python标准库外无第三方依赖。测试环境：Python 2.7。

	python youku.py urls...
	python youku.py --playlist url

安装
----

1. 安装git（非github用户应该只需要执行第一步Download and Install Git）

      http://help.github.com/set-up-git-redirect

2. 下载代码（Windows用户请在git-bash里执行）

        git clone git://github.com/iambus/youku-lixian.git

3. 安装Python 2.x（请下载最新的2.7版本。3.x版本不支持。）

      http://www.python.org/getit/

4. 在命令行里运行

        python youku.py 视频链接地址

注：不方便安装git的用户可以选择跳过前两步，在github网页上下载最新的源代码包（选择"Download as zip"或者"Download as tar.gz"）：

https://github.com/iambus/youku-lixian/downloads

统一下载
--------

	python video_lixian.py urls...
	python video_lixian.py --playlist url

单独下载
--------

也可以直接使用对应的脚本进行下载。比如：

	python youku.py urls...
	python youku.py --playlist url

其他下载
--------

本脚本完全按需编码（目前就我个人的需求）。如果想支持其他在线视频站点的下载，请在github里New Issue：

https://github.com/iambus/youku-lixian/issues

提交的时候请附上需要支持的链接。因为同一站点的不同页面的下载方式可能各不相同，为了减少开发和测试的工作量，一般只支持用户提交的链接。如果你发现某个新链接无法下载，请提交一个新的issue。


