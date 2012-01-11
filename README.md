youku-lixian
=============
优酷视频下载的Python脚本。顺便支持bilibili……

简介
----
从优酷网站上下载flv/mp4分段视频文件，并拼接。友情支持bilibili。
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

        python youku.py 视频连接地址

注：不方便安装git的用户可以选择跳过前两步，在github网页上下载最新的源代码包（选择"Download as zip"或者"Download as tar.gz"）：

https://github.com/iambus/youku-lixian/downloads

优酷下载
--------

python youku.py urls...
python youku.py --playlist url

bilibili下载
------------

python bilibili.py urls...

其他下载
--------

本脚本完全按需编码（目前就我个人的需求）。如果想支持其他在线视频站点的下载，请在github里New Issue：https://github.com/iambus/youku-lixian/issues。


