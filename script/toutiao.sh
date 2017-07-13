#/bin/sh
python_env='/home/wcy/env/bin/activate'
dir='/home/wcy/myspider'

if [ $# -eq 1 ];then
    date=`date -d "$1" +%Y%m%d`
elif [ $# -eq 0 ];then
    date=`date -d '-1 day' +%Y%m%d`
else
    echo '[ERROR] Wrong params number!'
    echo '[USAGE] $0 date'
    exit
fi

echo $date

source $python_env
cd $dir
scrapy crawl toutiao -a date=$date -o $dir/result/toutiao/$date.json -t json
