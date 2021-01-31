echo '切换到工作目录'
work_path=$(dirname $(readlink -f $0))
cd ./${work_path}

export LD_LIBRARY_PATH=${work_path}
./iat_sample