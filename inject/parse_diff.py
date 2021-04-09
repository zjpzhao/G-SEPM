# -*- coding: utf-8 -*-

# 用于判断错误注入的结果

import os
import numpy as np
import sys


stderr_file = "stderr.txt"
stdout_file = "stdout.txt"
output_file = "out.txt"
back_output = "back_output.txt"
diff_file = "diff.log"
golden_output = "golden/out.txt"
back_golden = "backup_golden_output.txt"
outcome_file = "outcome.txt"
basic_file = "basic.txt"

outcome = 0

metric = 0


# 从shell脚本读入程序返回值
para = int(sys.argv[1])
itera_time = int(sys.argv[2])
if os.path.exists(stderr_file):
    line_num = 0
    stdout = open(stdout_file, 'r')
    std_time = 0.0018
    for line in stdout.readlines():
        line_num += 1
        if line_num == 2:
            time = float(line.split()[-1][0:-1])
    size = os.path.getsize(stderr_file)
    if size != 0:
        outcome = 1
        metric = sys.maxsize
        print("======================error文件非空===========================")
    elif para != 0:
        outcome = 1
        metric = sys.maxsize
        print("=========================程序没有正确返回0==============================")
    # elif time > 0.0018 * 10:
    #     outcome = 1
    #     metric = sys.maxsize
    else:
        if os.path.getsize(diff_file) == 0:
            # Masked
            outcome = 2
        else:
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            outcome = 3
            # SDC difference
            f1 = open(output_file, 'r')  # 注错输出文件
            f2 = open(back_output, 'w')  # 注错输出的备份
            for line in f1.readlines():
                f2.write(line[0:-2].replace("\t", ","))
                f2.write("\n")
            f1.close()
            f2.close()

            f1 = open(golden_output, "r")  # 正确输出文件
            f2 = open(back_golden, "w")  # 正确输出的备份
            for line in f1.readlines():
                f2.write(line[0:-2].replace("\t", ","))
                f2.write("\n")
            f1.close()
            f2.close()

            golden_output = np.loadtxt(back_golden, delimiter=",")
            corrupted_output = np.loadtxt(back_output, delimiter=",")
            diff_matrix = corrupted_output - golden_output

            diff_sum = 0
            golden_sum = 0
            m, n = np.shape(diff_matrix)
            for i in range(m):
                for j in range(n):
                    diff_sum += np.square(diff_matrix[i, j])
                    golden_sum += np.square(golden_output[i, j])

            metric = np.sqrt(diff_sum / golden_sum)



f = open(outcome_file, 'a')
if outcome == 1:
    f.write("{0},{1},{2}\n".format(itera_time, "DUE", metric))
elif outcome == 2:
    f.write("{0},{1},{2}\n".format(itera_time, "Masked", metric))
else:
    f.write("{0},{1},{2}\n".format(itera_time, "SDC", metric))
f.close()



with open(stdout_file,'r',encoding="utf-8") as fstdout:
    with open(basic_file,'a',encoding="utf-8") as fbasic:
        line1=fstdout.readline()
        line1=fstdout.readline()
        line1=line1.split(": ")
        exetime=line1[1].strip()
        print(exetime)
        print(type(exetime))  
        fbasic.write(',')
        fbasic.write(exetime)
        fbasic.write('\n')