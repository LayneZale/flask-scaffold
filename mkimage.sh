cd ../
docker build -t cabits-harbor.chinaeast2.cloudapp.chinacloudapi.cn/cabits/cabits-converter-log-svr:"$1" .
docker login -u hp-zhangl -p Hongpu1232144 cabits-harbor.chinaeast2.cloudapp.chinacloudapi.cn
docker push cabits-harbor.chinaeast2.cloudapp.chinacloudapi.cn/cabits/cabits-converter-log-svr:"$1"
docker images|grep none|awk "{print $3}" |xargs docker rmi -f
