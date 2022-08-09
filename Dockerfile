FROM cabits-harbor.chinaeast2.cloudapp.chinacloudapi.cn/cabits/cabits:azure_base

# 复制项目
COPY .src/ /opt

# 设置编码
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# 安装运行环境
WORKDIR /opt
RUN apt install -y patchelf && pip3 install -r requirements.txt -i https://pypi.douban.com/simple

# 编译, 调试时请注释掉以下代码, 日志在容器根目录下的compile.log
RUN python3 ./compile/build.py

# 运行
EXPOSE 8000
CMD ["sh","/opt/run.sh"]
