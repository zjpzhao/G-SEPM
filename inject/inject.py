# -*- coding: utf-8 -*-

# 一次注错

import os, io, sys, re, math, random
import numpy as np

app_name = "correlation"
ptx_file = "correlation.ptx"
dryrun_before = "dryrun.out"
dryrun_file = "dryrun1.out"  # 删除多余内容后的文件
back_file = "correlation1.ptx"
temp_file = "temp.ptx"
basic_file = "basic.txt"


# 生成可以注错的指令行list
# 输出注错指令列表
def instruction_list():

    ins_list = []

    line_number = 0
    f = open(back_file,'r')

    for line in f.readlines():
        line_number += 1
        line.strip()
        # 删除每行首尾的空格
        analyze_line = line.strip()
        ana_ins = analyze_line.split(' ')

        if analyze_line.startswith('//') or analyze_line.startswith('.') or analyze_line.startswith(')') \
                or analyze_line.startswith('{') or analyze_line.startswith('}') or analyze_line == '' \
                or analyze_line.startswith('BB') or analyze_line.startswith('ret') or analyze_line.startswith('_') or analyze_line.startswith('st'):
            continue
        # analyze_line.startswith('ld.param') or
        elif analyze_line.startswith('@') or analyze_line.startswith('bra') or analyze_line.startswith('ld.param'):
            continue
        # 计算线程id的不注入错误
        elif ana_ins[-1].endswith('x;') or ana_ins[-1].endswith('y;'):
            continue
        #在线程号没有计算完之前不要注错   or 158 < line_number <177    or 93 < line_number < 115
        elif 1 < line_number < 33 or 108 < line_number < 130 or 205 < line_number < 232 or 263 < line_number < 284:
            continue
        # elif analyze_line.startswith('st'):
        #     continue
        # elif 54 < line_number < 98 or 143 < line_number < 187:
        #     ins_list.append(line_number)
            #continue
        else:
            ins_list.append(line_number)
    return ins_list


# 根据目的寄存器的位数，生成随机的注错值
# 输入：寄存器位数（32,64）
# 输出：随机的十六进制数

def random_bit(reg_digit):
    # 针对pred的情况
    if reg_digit == 1:
        ran_bit = random.randint(0, 1)
    else:
        ran_bit = random.randint(0, int(reg_digit)-1)  # 生成随机0-31，或者0-63的随机数数
    dec_num = str(int(math.pow(2, ran_bit))).replace(".0", "")  # float转化为str，str去除.0
    fault_value = hex(np.compat.long(str(dec_num), 10))  # 转化为十六进制
    fault_value = str(fault_value).strip('L')
    return fault_value, ran_bit

# 循环中注入错误，在第几次循环注入
# 输入：线程数目，目的是为了计算循环次数
# 输出：随机注入的循环次数
def random_loop_time(thread_num,div):
    loopdiv = div
    loop_time = thread_num/div
    ran_loop = random.randint(1,thread_num/div)
    return loopdiv,loop_time , ran_loop

# 看注错的行号是否在循环内
# 输入：注错的行号
# 改！！！！
def in_loop(target_line):
    inloop = '0'
    loop_reg = 'null'
    if 45 < int(target_line) < 101:
        inloop = '1'
        loop_reg = '%r11'
        return loop_reg,inloop
    elif 144 < int(target_line) < 192:
        inloop = '2'
        loop_reg = '%r12'
        return loop_reg,inloop
    elif 308 < int(target_line) < 352:
        inloop = '4_2'
        loop_reg = '%r22'
    # elif 300 < int(target_line) < 308 or 352 < int(target_line) < 360:
    #     inloop = '4_1'
    #     loop_reg = '%r21'

    return loop_reg,inloop



# 确定错误注入的随机行号
def inject_line_num(ins_list):
    target_line = random.choice(ins_list)
    return target_line


# 二维线程时的情况
def random_thread2(thread_x, thread_y):
    random_x = random.randint(1, thread_x - 1)
    random_y = random.randint(1, thread_y - 1)
    return random_x, random_y


# 一维线程时的情况
def random_thread1(thread_x):
    random_x = random.randint(1, thread_x - 1)
    return random_x


# 获取备份ptx中的标签数量
def get_label():
    f1 = open(back_file, 'r')
    label_num = 0
    for line in f1.readlines():
        if line.startswith('BB0_'):
            label_num += 1
    f1.close()
    return label_num

# 获取备份ptx中的kernel数量
def get_kernel_info():
    f1 = open(back_file, 'r')
    line_num = 0
    kernel_dict = {}
    kernel_num = 0
    for line in f1.readlines():
        line_num += 1
        analyze_line = line.strip()
        # 判断如果是否是kernel的名
        if analyze_line.startswith('// .globl'):
            kernel_name = analyze_line.split()[-1]  # kernel的名称
            kernel_num += 1
            kernel_dict.update([(kernel_num, kernel_name)])
    return kernel_num, kernel_dict

# 根据注错行号判断kernel name,以及最后一个参数last_param
# last_param、行号  需要自己去ptx文件中找,每个benchmark更改
# 改！！！！改！！！！改！！！！改！！！！改！！！！


def get_kernel_name_param(target_line, kernel_dict):
    kernel_name = ''
    last_param = ''
    kernel_id = 0
    thread_x_reg = ''
    thread_y_reg = ''
    if 1 < int(target_line) < 108:
        kernel_id = 1
        kernel_name = kernel_dict.get(1)
        last_param = '[_Z11mean_kernelPfS_Pd_param_2]'

        thread_x_reg = '%r1'
        thread_y_reg = ''
    #elif 94 < int(target_line) < 179:
    elif 108 < int(target_line) < 205:
        kernel_id = 2
        kernel_name = kernel_dict.get(2)
        last_param = '[_Z10std_kernelPfS_S_Pd_param_3]'
        thread_x_reg = '%r1'
        thread_y_reg = ''
    elif 205 < int(target_line) < 263:
        kernel_id = 3
        kernel_name = kernel_dict.get(3)
        last_param = '[_Z13reduce_kernelPfS_S_Pd_param_3]'
        thread_x_reg = '%r1'
        thread_y_reg = '%r3'
    else:
        kernel_id = 4
        kernel_name = kernel_dict.get(4)
        last_param = '[_Z11corr_kernelPfS_Pd_param_2]'
        thread_x_reg = '%r1'
        thread_y_reg = ''
    # else:
    #     kernel_id = 3
    #     kernel_name = kernel_dict.get(3)
    #     last_param = '[_Z12covar_kernelPfS_Pd_param_2]'

    return kernel_id , kernel_name, last_param, thread_x_reg, thread_y_reg


# 输入：注错的行号
# 输出：指令类型，位数（32,64），寄存器类型（u,b,s）,目的寄存器（%r11）
# 功能：解析注错行的指令
def analyze_ins(target_line):
    f = open(temp_file, 'r')
    # cvt.s64.s32 %rd13, %r6;
    for line in f.readlines():
        split_line = line.split()  # 按照空格划分行
        # 不分析kernel名字和标签的行
        if len(split_line) > 2:
            # 定位到要插入的指令
            if split_line[0] == str(target_line):
                ins_str = split_line[1]  # 包含opcode的串
                des_str = split_line[2]  # 包含目的寄存器的串
                op_ins = split_line[1].split('.')
                #如果是cvt类型，需要注意
                if split_line[1].split('.')[0] == 'cvt':
                    after_change = re.sub("[^0-9]", "", op_ins[1])

                # 处理ins_str串
                ins_str_list = ins_str.split('.')  # ld.param.u64  mov.u32
                # mov u32
                if len(ins_str_list) == 2:
                    ins_opcode = ins_str_list[0] # mov,mad,ld....
                    reg_str = ins_str_list[-1]  # s32,u32,s64,b32,f32
                    if reg_str == "pred":
                        reg_digit = "1"
                        reg_type = "pred"
                    else:
                        reg_digit = re.sub("[^0-9]", "", reg_str)  # 目的寄存器的位数
                        reg_type = re.sub("[^a-z]", "", reg_str)  # 目的寄存器的类型
                # ld param u64
                else:
                    ins_opcode = ins_str_list[0]  # mov,mad,ld....
                    reg_str = ins_str_list[-1]  # s32,u32,s64,b32,f32
                    if ins_opcode == "setp":
                        reg_digit = "1"
                        reg_type = "pred"
                    elif ins_opcode == "mul" or ins_opcode == "mad":
                        if ins_str_list[1] == "wide":
                            reg_digit = str(int(re.sub("[^0-9]", "", reg_str)) * 2)
                        else:
                            reg_digit = re.sub("[^0-9]", "", reg_str)
                        reg_type = re.sub("[^a-z]", "", reg_str)  # 目的寄存器的类型
                    else:
                        reg_digit = re.sub("[^0-9]", "", reg_str)  # 目的寄存器的位数
                        reg_type = re.sub("[^a-z]", "", reg_str)  # 目的寄存器的类型

                # 处理des_str串
                des_reg = des_str.split(',')[0]
                if split_line[1].split('.')[0] == 'cvt':
                    reg_digit = re.sub("[^0-9]", "", op_ins[1])
                return ins_opcode, reg_digit, reg_type, des_reg, reg_str


# 输入：
# 输出：
# 功能：针对一个kernel，主要二维线程注入错误
def inject_one_fault(target_line,  # 错误注入的行
                     thread_num,   # 几维线程
                     target_x, target_y,    # 随机线程
                     reg_type,        # 注错的指令类型
                     fault_value,       # 注错的值
                     reg_digit,         # 目的寄存器的位数
                     dest_reg,          # 指令目的寄存器
                     label_num,         # 现有标签的个数
                     instruction_type,   # 计算线程的寄存器类型，s32
                     reg_str,             # 结果寄存器类型
                     last_param,           # 参数
                     ran_loop,             # 第几次循环注入
                     inloop,                  #是否在循环里
                     loop_time,              #总循环次数
                     loop_reg,                #循环寄存器
                     loopdiv,                 #循环除数
                     thread_x_reg,
                     thread_y_reg,
                     kernel_id
                     # des_reg_type             #目的寄存器类型
                     ):
    line_num = 0  # 记录行数
    pred_reg_num = 0  # 记录pred寄存器原来的数量
    rd_reg_num = 0  #记录S32寄存器原来的个数
    pfile = open(ptx_file, "w")
    bfile = open(back_file, 'r')


    for line in bfile.readlines():
        line_num += 1  # 记录行数

        # 注错不在循环内
        if inloop == '0':

            if thread_num == 1:
                # 修改pred的值
                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]  # 获取到寄存器的类型，eg .pred .f32
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_pred = int(pred_reg_num) + 1  # 增加1个断言寄存器
                        str_1 = ".reg .pred   %p<" + str(after_pred) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    elif type_item == ".b64":
                        rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_rd = int(rd_reg_num) + 1  # 增加1个rd寄存器
                        str_1 = ".reg .b64   %rd<" + str(after_rd) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    else:
                        pfile.write(line)  # 其他类型直接写入

                # 如果是要注入错误的行
                elif line_num == int(target_line):
                    pfile.write(line)  # 先将当前指令写入ptx文件
                    # target_x, target_y = random_thread2(thread_x, thread_y)  # 生成的随机的线程数 int,int
                    # 如果目的寄存器是pred类型的情况
                    if reg_type == "pred":
                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + ", " + thread_x_reg + ", " + str(target_x) + ";"
                        insert_str2 = "@!%p" + str(pred_reg_num) + "  bra BB0_100;"
                        # insert_str3 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str4 = "st.global.pred [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str5 = "xor.pred    " + str(dest_reg) + ", " + str(dest_reg) + ", 0x1;"
                        # insert_str6 = "st.global.pred [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str7 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        # pfile.write('       ' + insert_str3 + '\n')
                        # pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write(insert_str7 + '\n')
                        pass
                    # 不是pred的指令
                    else:

                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + ", " + thread_x_reg + ", " + (str(target_x)) + ";"
                        insert_str2 = "@!%p" + (str(pred_reg_num)) + "  bra BB0_100;"
                        insert_str3 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        insert_str4 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        # if des_reg_type.startswith('s'):
                        #     insert_str5 = "xor.s" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(
                        #         dest_reg) + ", " + str(fault_value) + ";"
                        # else:
                        insert_str5 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(dest_reg) + ", " + str(fault_value) + ";"
                        insert_str6 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str7 = "BB0_100:"



                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        pfile.write('       ' + insert_str6 + '\n')
                        pfile.write(insert_str7 + '\n')

                else:
                    pfile.write(line)
            # 线程是2维
            else:
                # 修改pred的值
                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]  # 获取到寄存器的类型，eg .pred .f32
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_pred = (int(pred_reg_num) + 3)  # 增加三个断言寄存器
                        str_1 = ".reg .pred   %p<" + str(after_pred) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    elif type_item == ".b64":
                        rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_rd = (int(rd_reg_num) + 1)  # 增加1个rd寄存器
                        str_1 = ".reg .b64   %rd<" + str(after_rd) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    else:
                        pfile.write(line)  # 如果是.f32 .s32 .s64 类型直接写入

                # 如果是注入错误的行
                elif line_num == int(target_line):
                    # 先将当前指令写入ptx文件
                    pfile.write(line)
                    # target_x, target_y = random_thread2(thread_x, thread_y)  # 生成的随机的线程数 int,int
                    # 如果目的寄存器是pred类型的情况
                    if reg_type == "pred":
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1
                        # 插入语句的时候，要注意比较线程id的寄存器是不是r1和r2，需要根据情况修改。

                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + ", " + thread_x_reg + ", " + (str(target_x)) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " " + "%p" + (str(temp_pred1)) \
                                      + ", " + thread_y_reg + ", " + (str(target_y)) + ";"


                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + str(pred_reg_num) + ", %p" + (
                            str(temp_pred1)) + ";"
                        insert_str4 = "@!%p" + (str(temp_pred2)) + "  bra BB0_100;"

                        # insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str6 = "st.global.s32 [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str7 = "xor.pred    " + str(dest_reg) + ", " + str(dest_reg) + ", 0x1;"
                        #insert_str8 = "st.global.s32 [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        # pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        #pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')
                        pass
                    # 不是pred的指令
                    else:
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1
                        # “如果是注入错误的行”情况下，插入语句的时候，要注意比较线程id的寄存器是不是r1和r2，需要根据情况修改。
                        # 插入加载参数地址的语句也需要注意，更改参数的名字
                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + ", " + thread_x_reg + ", " + (str(target_x)) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " " + "%p" + (str(temp_pred1)) \
                                      + ", " + thread_y_reg + ", " + (str(target_y)) + ";"


                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + str(pred_reg_num) + ", %p" + (
                            str(temp_pred1)) + ";"

                        insert_str4 = "@!%p" + (str(temp_pred2)) + "  bra BB0_100" ";"
                        insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        insert_str6 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"

                        # if des_reg_type.startswith('s'):
                        #     insert_str7 = "xor.s" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(
                        #         dest_reg) + ", " + str(fault_value) + ";"
                        # else:
                        #     insert_str7 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(
                        #         dest_reg) + ", " + str(fault_value) + ";"

                        insert_str7 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(dest_reg) + ", " \
                                      + str(fault_value) + ";"
                        insert_str8 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100" ":"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')

                else:
                    pfile.write(line)  # 不是目标行，直接写入


        #注错行在循环内
        else:
            if thread_num == 2:
                # 修改pred、和S32的值
                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]  # 获取到寄存器的类型，eg .pred .f32
                    # p寄存器个数加五
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_pred = (int(pred_reg_num) + 5)  # 增加五个断言寄存器
                        str_1 = ".reg .pred   %p<" + str(after_pred) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    elif type_item == ".b64":
                        rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_rd = (int(rd_reg_num) + 1)  # 增加1个rd寄存器
                        str_1 = ".reg .b64   %rd<" + str(after_rd) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    # 否则直接写入
                    else:
                        pfile.write(line)  # 其他类型直接写入
                # 如果是要注入错误的行
                elif line_num == int(target_line):
                    print("====================共"+ str(loop_time) +"次循环，在第" + str(ran_loop) + "次注入===================")
                    pfile.write(line)  # 先将当前指令写入ptx文件
                    # target_x, target_y = random_thread2(thread_x, thread_y)  # 生成的随机的线程数 int,int
                    # 如果目的寄存器是pred类型的情况
                    if reg_type == "pred":
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1
                        temp_pred3 = int(temp_pred2) + 1
                        temp_pred4 = int(temp_pred3) + 1
                        #需要修改下面语句中的r17，是控制循环的语句
                        # insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #               + ", %r17, " + str((ran_loop-1)*8) + ";"
                        # insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #               + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"

                        if loop_reg == '%r11' or loop_reg == '%r12' or loop_reg == '%r22':
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv + 1) + ";"
                        else:
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + ", " + thread_x_reg + ", " + str(target_x) + ";"

                        insert_str3 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred2) \
                                       + ", " + thread_y_reg +  ", " + str(target_y) + ";"

                        insert_str4 = "and.pred    %p" + (str(temp_pred3)) + ", %p" + (str(temp_pred1)) \
                                       + ", %p" + (str(temp_pred2)) + ";"
                        insert_str5 = "and.pred    %p" + (str(temp_pred4)) + ", %p" + (str(temp_pred3)) \
                                       + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str6 = "@!%p" + (str(temp_pred4)) + " bra BB0_100;"
                        # insert_str7 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str8 = "st.global.s32 [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str9 = "xor.pred " + (str(dest_reg)) + ", " + str(dest_reg) + ", 0x1;"
                        #insert_str10 = "st.global.s32 [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str11 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        pfile.write('       ' + insert_str6 + '\n')
                        # pfile.write('       ' + insert_str7 + '\n')
                        # pfile.write('       ' + insert_str8 + '\n')
                        pfile.write('       ' + insert_str9 + '\n')
                        #pfile.write('       ' + insert_str10 + '\n')
                        pfile.write(insert_str11 + '\n')
                        pass
                    # 不是pred的指令
                    else:
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1
                        temp_pred3 = int(temp_pred2) + 1
                        temp_pred4 = int(temp_pred3) + 1
                        # insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #               + ", %r17, " + str((ran_loop-1) * 8) + ";"
                        # insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #               + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"

                        if loop_reg == '%r11' or loop_reg == '%r12' or loop_reg == '%r22':
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv + 1) + ";"
                        else:
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + ", " + thread_x_reg + ", " + (str(target_x)) + ";"

                        insert_str3 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred2) \
                                      + ", " + thread_y_reg + ", " + (str(str(target_y))) + ";"

                        insert_str4 = "and.pred    %p" + (str(temp_pred3)) + ", %p" + (str(temp_pred1)) \
                                      + ", %p" + (str(temp_pred2)) + ";"
                        insert_str5 = "and.pred    %p" + (str(temp_pred4)) + ", %p" + (str(temp_pred3)) \
                                      + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str6 = "@!%p" + (str(temp_pred4)) + " bra BB0_100;"
                        insert_str7 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        insert_str8 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," \
                                      + str(dest_reg) + ";"

                        # if des_reg_type.startswith('s'):
                        #     insert_str9 = "xor.s" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(
                        #         dest_reg) + ", " + str(fault_value) + ";"
                        # else:
                        #     insert_str9 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(
                        #         dest_reg) + ", " + str(fault_value) + ";"

                        insert_str9 = "xor.b" + str(reg_digit) + "    " +(str(dest_reg)) + ", " + (str(dest_reg)) \
                                      + ", " + str(fault_value) + ";"
                        insert_str10 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + \
                                      str(dest_reg) + ";"
                        insert_str11 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        pfile.write('       ' + insert_str8 + '\n')
                        pfile.write('       ' + insert_str9 + '\n')
                        pfile.write('       ' + insert_str10 + '\n')
                        pfile.write(insert_str11 + '\n')
                else:
                    pfile.write(line)

            # 线程是1维
            else:
                # 修改pred的值
                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]  # 获取到寄存器的类型，eg .pred .f32
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_pred = (int(pred_reg_num) + 3)  # 增加五个断言寄存器
                        pfile.write(line.replace(str(pred_reg_num), str(after_pred)))  # 将修改后的pred写入ptx
                        # s32寄存器个数加一，记录循环次数
                    elif type_item == ".b64":
                        rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  # 获取当前pred寄存器的个数
                        after_rd = (int(rd_reg_num) + 1)  # 增加1个rd寄存器
                        str_1 = ".reg .b64   %rd<" + str(after_rd) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    # 否则直接写入
                    else:
                        pfile.write(line)  # 如果是.f32 .s32 .s64 类型直接写入
                # 如果是注入错误的行
                elif line_num == int(target_line):
                    print("====================共"+ str(loop_time) +"次循环，在第" + str(ran_loop) + "次注入===================")
                    pfile.write(line)  # 先将当前指令写入ptx文件
                    # target_x, target_y = random_thread2(thread_x, thread_y)  # 生成的随机的线程数 int,int
                    # 如果目的寄存器是pred类型的情况
                    if reg_type == "pred":
                        # p寄存器编号
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(pred_reg_num) + 2
                        # 需要修改下面语句中的r17，是控制循环的语句
                        # insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #               + ", %r17, " + str((ran_loop - 1) * 8) + ";"
                        #

                        if loop_reg == '%r11' or loop_reg == '%r12' or loop_reg == '%r22':
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv + 1) + ";"
                        else:
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"

                        # insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #               + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"
                        # %r1要改，根据每个benchmark的不同
                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + ", " + thread_x_reg + "," + (str(target_x)) + ";"
                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + (str(temp_pred1)) + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str4 = "@!%p" + (str(temp_pred2)) + " bra BB0_100;"
                        # insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str6 = "st.global.s32 [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"

                        insert_str7 = "xor.pred" + (str(dest_reg)) + ", " + (str(dest_reg)) + ", 0x1;"
                        #insert_str8 = "st.global.s32 [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        # pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        #pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')

                    # 不是pred的指令
                    else:

                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(pred_reg_num) + 2

                        # if loop_reg == '%r13':
                        #     insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #                   + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv - 2048) + ";"
                        # else:
                        #     insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                        #                   + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"

                        if loop_reg == '%r11' or loop_reg == '%r12' or loop_reg == '%r22':
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv + 1) + ";"
                        else:
                            insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                          + ", " + loop_reg + ", " + str((ran_loop - 1) * loopdiv) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + ", " + thread_x_reg + ", " + (str(target_x)) + ";"
                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + (str(temp_pred1)) + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str4 = "@!%p" + (str(temp_pred2)) + " bra BB0_100;"
                        insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        insert_str6 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        #insert_str7 = "xor." + str()
                        # if des_reg_type.startswith('s'):
                        #     insert_str7 = "xor.s" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(
                        #         dest_reg) + ", " + str(fault_value) + ";"
                        # else:
                        #     insert_str7 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(
                        #         dest_reg) + ", " + str(fault_value) + ";"
                        insert_str7 = "xor.b" + str(reg_digit) + "    " +(str(dest_reg)) + ", " + (str(dest_reg)) + ", " + str(fault_value) + ";"
                        insert_str8 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')
                else:
                    pfile.write(line)  # 不是目标行，直接写入

    pfile.close()
    bfile.close()


def main():
    itera_time = int(sys.argv[1])  # 获取迭代次数
    thread_num = 1
    thread_x = 512     #——————修改——————
    thread_y = 512     #——————修改——————
    instruction_type = "s32"
    ran_loop = 0
    loop_time = 0
    loop_reg = 'null'
    loopdiv = 0
    target_x = 0
    target_y = 0
    thread_x_reg =''
    thread_y_reg = ''
    loop_ceng = 1
    # 1 make keep and 2 make dry 之后
    # 3 删除dryrun多余的行 read_line
    # 4 备份，一次 back_ptx
    # 5 生成temp.ptx，多次错误注入只进行一次 read_ptx
    # 6 获取标签的数量
    label_num = get_label()
    # 7 注错的list
    ins_list = instruction_list()
    # 8 注错的行
    target_line = inject_line_num(ins_list)
    # 9 获取kernel num和kernel name
    kernel_num, kernel_dict = get_kernel_info()
    kernel_id , kernel_name, last_param,thread_x_reg ,thread_y_reg= get_kernel_name_param(target_line, kernel_dict)
    print(str(kernel_name) + "-----" + str(last_param))
    # 10 分析注错指令
    ins_opcode, reg_digit, reg_type, des_reg, reg_str = analyze_ins(target_line)
    # 11 生成注错的值
    fault_value, bit = random_bit(reg_digit)

    # 13 看在第几个kernel中，以此判断线程的维数
    # target_x , target_y = random_thread2(thread_x,thread_y)
    if kernel_id == 1 or kernel_id == 2 or kernel_id == 4:
        target_x = random_thread1(thread_x)
    elif kernel_id == 3:
        target_x,target_y = random_thread2(thread_x,thread_y)
    #target_x = random_thread1(thread_x)
    # if kernel_id == 1 :
    #     thread_num = 1
    #     target_x = random_thread1(thread_x)
    # else:
    #     thread_num = 1
    #     target_x = random_thread1(thread_x)

    #

    # 12 是否在循环内,注错循环次数
    #loop = '0'
    loop_reg,inloop = in_loop(target_line)
    if inloop == '1':
        loopdiv,loop_time , ran_loop = random_loop_time(thread_x,16)
    elif inloop == '2':
        loopdiv, loop_time, ran_loop = random_loop_time(thread_x, 8)
    elif inloop == '4_2':
        loop_ceng = 2
        loopdiv,loop_time,ran_loop = random_loop_time(thread_x,8)
    # elif inloop == '4_1':
    #     loop_ceng = 2
    #     loopdiv,loop_time,ran_loop = random_loop_time(511-target_x,1)
    # elif inloop == '2':
    #     loopdiv,loop_time , ran_loop = random_loop_time(thread_x,8)


    # 12 注错
    #target_x, target_y = random_thread2(thread_x, thread_y)
    inject_one_fault(target_line, thread_num, target_x, target_y, reg_type, fault_value, reg_digit, des_reg,
                     label_num, instruction_type,reg_str,last_param,ran_loop,inloop,loop_time,loop_reg,loopdiv,thread_x_reg,thread_y_reg,kernel_id)
    f = open(basic_file, 'a')
    f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}".format(itera_time, app_name, kernel_name, target_x,
                                                                         target_y, bit, fault_value, target_line,
                                                                         ins_opcode, reg_digit, reg_type, des_reg,ran_loop))
    f.close()


if __name__ == "__main__":
    main()
