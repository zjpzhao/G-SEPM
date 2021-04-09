#!/bin/bash
#export PATH=$PATH:/usr/local/cuda/bin
#export LD_LIBRARY_PATH=/usr/local/cuda-7.0/bin/lib64:$LD_LIBRARY_PATH
#变量赋值：各种输出文件
output_file="out.txt"
golden_file="golden"
source_file="2mm.cu"
executable_file="2mm"
executable_dry="dryrun1.out"
ptx_file="2mm.ptx"
back_file="2mm1.ptx"
dry_file="dryrun.out"
stdout_file="golden_stdout.txt"
stderr_file="golden_stderr.txt"
result_dir="result"

# compile all
make all
# -d
# Standard output directory
if [ ! -d "$golden_file" ];then
    printf "===== Create golden dir =====\n"
    mkdir golden
else
    printf "=====Golden output file have existed=====\n"
fi

# Create golden_stdout.txt and golden_stderr.txt
printf "===== Create golden_stdout.txt and golden_stderr.txt =====\n"
./$executable_file >golden_stdout.txt 2>golden_stderr.txt

# if golden_stdout.txt and golden_stderr.txt in current directory
if [ -f "$stdout_file" ]&&[ -f "$stderr_file" ];then
    mv -f golden_stdout.txt golden/golden_stdout.txt
    mv -f golden_stderr.txt golden/golden_stderr.txt
    printf "===== golden_stdout.txt and golden_stderr.txt move to golden =====\n"
else
    printf"=====golden_stdout.txt or golden_stderr.txt don't exist=====\n"
fi

# Run correctly
./$executable_file
printf "===== Run application correctly =====\n"

# if there are any output files in the current directory
if [ -f "$output_file" ];then
    mv -f out.txt golden/out.txt
    printf "===== out.txt Move to golden =====\n"
else
    printf "===== No output file ====\n"
fi
#删除所有设置所生成的所有的output与中间文件。
make clobber

# Modify the compile file
make keep
make dry

# Before Injection
python common_function.py
printf "delete_line back_ptx read_ptx"



if [ ! -d "$result_dir" ];then
    mkdir $result_dir
    printf "===== result created ====\n"
else
printf "===== result file have exited ====\n"
fi

# Set times of injection
# inject_num=5
middle="_midfile"
rm basic_reverse.txt
start_time=$(date +%s)
for i in $(seq 1 1000)
do
    printf "**********************************************THE $i INJECTION*****************************************\n"

    #inject one fault
    python inject.py $i;
    file_name=$i$middle
    sudo cp $ptx_file $result_dir/$file_name
  #如果dryrun1.out是可执行文件，执行它
    if test -x $executable_dry ; then
        ./$executable_dry
        OP_MODE=$?
    else
        printf "===== Increase executable of dryrun1.out =====\n"
        chmod +x $executable_dry
        ./$executable_dry
        OP_MODE=$?
    fi
    echo $i,>> reverse.txt
    # Create sdtout.txt and stderr.txt
    printf "===== Create sdtout.txt and stderr.txt =====\n"
    # timeout 5s ./$executable_file 1>stdout.txt 2>stderr.txt || [ $? -eq 124 ] && echo timeouted
    
    timeout 5s ./$executable_file 1>stdout.txt 2>stderr.txt
    if [[ $? == "124" ]]
    then
        echo timeouted_____________________________________________________________________________________________________________________________________________
        echo $i,DUE,hang>> DUE.txt
        echo $i,DUE,hang>> outcome.txt
        echo ,5s>> basic.txt
    else
        printf "===== Create out.txt =====\n"
        # ./$executable_file
        printf "===== Create diff.log =====\n"
        diff out.txt golden/out.txt>diff.log
        # after injection
        python parse_diff.py $OP_MODE $i
    fi

    # printf "===== Create out.txt =====\n"
    # ./$executable_file
    # printf "===== Create diff.log =====\n"
    # diff out.txt golden/out.txt>diff.log

    # # after injection
    # python parse_diff.py $OP_MODE $i
done
end_time=$(date +%s)
cost_time=$[ $end_time-$start_time ]
echo $cost_time
echo "build kernel time is $(($cost_time/60))min $(($cost_time%60))s"
# python merge_reverse.py
