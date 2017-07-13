#/bin/sh
python='/usr/local/bin/python'
dir='/Users/wuchengyi/Code/myspider'

if [ $# -eq 1 ];then
    date=$1
elif [ $# -eq 0 ];then
    date=$(date -v -1d '+%Y%m%d')
else
    echo '[ERROR] Wrong params number!'
    echo '[USAGE] $0 20170101'
    exit
fi

echo $date

cd $dir
scrapy crawl weixin -a date=$date -o $dir/result/weixin/$date.json -t json
