

# -*- coding: utf-8 -*-
# 根据ptx，数据依赖图以及指令的标签生成指令特征
# 输入：ptx, dep_list.txt, con_result.txt（手动统计生成）
# 输出：all_feature.txt
# 修改：in_loop,getloop,getbra
import re

file1 = "correlation1.ptx" # 存在
file4 = "dep_list_processed.txt"      # 存在
file7 = "result_test.txt"  # 存在

file2 = "ins.txt"          # 生成
file3 = "ins_feature.txt"   # 生成
file5 = "all_feature.data"  # 生成
file8 = "line_feature.data"    #生成
file6 = "ins2.txt"          # 生成

#zjp
insert_line1 = 19
insert_line2 = 120
dep_list_processed="dep_list_processed.txt"



# 根据PTX获取指令表
# 格式：line_num ins_type  dest_reg_type1  dest_reg_bit  operand_num  dest_reg_type2
def get_ins():
    line_num = 0  # 行号
    f1 = open(file1, 'r')
    f2 = open(file2, 'w')

    for line in f1.readlines():
        line_num += 1
        # 删除每行首尾的空格
        analyze_line = line.strip()
        # print(analyze_line)
        # 判断如果是否是kernel的名,并将其写入temp.ptx
        if analyze_line.startswith('// .globl'):
            continue
        if analyze_line == "":
            continue
        if analyze_line.startswith('//'):
            continue
        if analyze_line.startswith('.'):
            continue
        if analyze_line.startswith('BB0'):
            continue
        if analyze_line.startswith('BB1'):
            continue
        if analyze_line.startswith('BB2'):
            continue
        if analyze_line.startswith('BB3'):
            continue
        if analyze_line.startswith('(') or analyze_line.startswith(')'):
            continue
        if analyze_line.startswith('}') or analyze_line.startswith('{'):
            continue
        # if analyze_line.startswith('@'):
        #     continue
        if analyze_line.startswith('ret'):
            continue
        # 分支指令没有目的寄存器，不分析
        if analyze_line.startswith('bra'):
            continue
        else:
            # print(analyze_line.split())
            f2.write(str(line_num))  # 写入行号
            # 按空格划分
            ins_num = len(analyze_line.split())
            # ins_str = analyze_line.split()[0].split('.')[0]
            # 指令串
            ins_str = analyze_line.split()[0]
            # 目的寄存器串
            reg_str = analyze_line.split()[1]
            # r 或者 rd
            reg_operand = re.sub('[0-9]', '', reg_str.replace(',', '').replace('%', ''))
            # 指令操作符
            ins_operand_str = ins_str.split('.')[0]

            if ins_str.startswith('@'):
                # ins_operand = re.sub("[A_Za-z0-9]", "", ins_operand_str)
                ins_operand = '@'
                ins_type = re.sub("[^A_Za-z0-9]", "", ins_operand_str)
                ins_bit = "1"
            elif ins_str.startswith('and'):
                ins_operand = ins_str.split('.')[0]
                ins_type = ins_str.split('.')[-1]
                ins_bit = '1'
            else:
                ins_operand = ins_operand_str
                ins_type_str = ins_str.split('.')[-1]
                ins_type = re.sub("[0-9]", "", ins_type_str)
                ins_bit = re.sub("[^0-9]", "", ins_type_str)
            # 行号 指令操作数 目的寄存器类型 目的寄存器的位数 （1,2元操作）
            f2.write("\t" + ins_operand + "\t" + ins_type + "\t" + ins_bit + "\t" + str(ins_num - 2) + "\t" +
                     reg_operand + "\n")  # 写入指令行

    f1.close()
    f2.close()


# 获取指令表,删除没有用的行
# 格式：line_num ptx_line
def get_ins2():
    line_num = 0  # 行号
    f1 = open(file1, 'r')
    f2 = open(file6, 'w')

    for line in f1.readlines():
        line_num += 1
        # 删除每行首尾的空格
        analyze_line = line.strip()
        # 判断如果是否是kernel的名,并将其写入temp.ptx
        if analyze_line.startswith('// .globl'):
            f2.write(str(line_num) + " ")  # 写入行号
            kernel_name = analyze_line.split()[-1]  # kernel的名称
            f2.write(kernel_name + "\n")  # 文件的头部是kernel名字
        if analyze_line == "":
            continue
        if analyze_line.startswith('//'):
            continue
        if analyze_line.startswith('.'):
            continue
        if analyze_line.startswith('(') or analyze_line.startswith(')'):
            continue
        if analyze_line.startswith('}') or analyze_line.startswith('{'):
            continue
        # if analyze_line.startswith('@'):
        #     continue
        if analyze_line.startswith('ret'):
            continue
        else:
            f2.write(str(line_num))  # 写入行号
            f2.write(" " + analyze_line + "\n")  # 写入指令行
    f1.close()
    f2.close()


# 获取静态指令特征
# 输入：ins.txt
# 输出：ins_feature.txt
# 输出列表：ins_num 操作数个数,整型加法或减法,浮点加减法,整型乘法除法,浮点乘除法,比较指令,逻辑运算(用于控制),逻辑运算(普通),
#             左移,右移,取值,目的寄存器的bit

def get_ins_feature():
    f1 = open(file2, 'r')  # ins.txt
    f2 = open(file3, 'w')  # ins_feature.txt

    for line in f1.readlines():
        analy_line = line.split()
        s = ''
        # 1 行号
        s += analy_line[0] + ' '
        # 2 操作数个数
        s += analy_line[-2] + ','
        # 3 整型加法或减法
        if (analy_line[1] == 'add' or analy_line[1] == 'sub') and (analy_line[2] == 'u' or analy_line[2] == 's'):
            s += '1,'
        else:
            s += '0,'
        # 4 浮点加减法
        if (analy_line[1] == 'add' or analy_line[1] == 'sub') and (analy_line[2] == 'f'):
            s += '1,'
        else:
            s += '0,'
        # 5 整型乘法除法
        if (analy_line[1] == 'mul' or analy_line[1] == 'div') and (analy_line[2] == 'u' or analy_line[2] == 's'):
            s += '1,'
        else:
            s += '0,'
        # 6 浮点乘除法
        if (analy_line[1] == 'mul' or analy_line[1] == 'div' or analy_line[1] == 'fma') and (analy_line[2] == 'f'):
            s += '1,'
        else:
            s += '0,'
        # 7 比较指令
        if analy_line[1] == 'setp':
            s += '1,'
        else:
            s += '0,'
        # 8 逻辑运算断言逻辑运算，用于控制流指令，因为控制流指令没有目标寄存器
        if (analy_line[1] == 'and' or analy_line[1] == 'or' or analy_line[1] == 'xor' or analy_line[1] == 'or') and \
                analy_line[2] == 'pred':
            s += '1,'
        else:
            s += '0,'
        # 9 逻辑运算
        if (analy_line[1] == 'and' or analy_line[1] == 'or' or analy_line[1] == 'xor' or analy_line[1] == 'or') and \
                analy_line[2] != 'pred':
            s += '1,'
        else:
            s += '0,'
        # 10 左移位指令
        if analy_line[1] == 'shl':
            s += '1,'
        else:
            s += '0,'
        # 11 右移位指令
        if analy_line[1] == 'shr':
            s += '1,'
        else:
            s += '0,'
        # 12 取值指令
        if analy_line[1] == 'ld':
            s += '1,'
        else:
            s += '0,'
        # 13 目的寄存器的bit数
        if len(analy_line) == 6:
            s += analy_line[3] + ','
        else:
            s += '0,'

        # 14 是否在循环内
        s += in_loop(analy_line[0])

        s += '\n'
        f2.write(s)

    f1.close()
    f2.close()


# 从文件中获取指令静态特征
# 输入：ins_feature.txt
def ins_feature(target_ins):
    # ins_feature.txt
    f = open(file3, 'r')
    for line in f.readlines():
        analy_line = line.split()
        # print(analy_line[0])
        # print(analy_line[1])
        if analy_line[0] == target_ins:
            return analy_line[1]
    return 'N'


# 1 获取应用中所有的maked指令
# 输入：ins.txt
# 输出：ins_list 所有Masked指令行号
def get_masked_ins():
    # ins.txt
    f1 = open(file2, 'r')
    ins_list = []

    for line in f1.readlines():
        a_line = line.split()
        # print(a_line)
        # 如果指令是不是用于断言的and和or
        if (a_line[1] == 'and' or a_line[1] == 'or') and (a_line[2] != 'pred'):
            ins_list.append(a_line[0])
        # 移位指令
        elif a_line[1] == 'shl':
            ins_list.append(a_line[0])
    f1.close()
    # 指令列表
    return ins_list


# 2 地址指令列表
# 输入：ins.txt
# 输出：address_list 地址相关指令的列表
def address_ins():
    # ins.txt
    f1 = open(file2, 'r')
    address_list = []
    # bit_list = []
    for line in f1.readlines():
        # 按照空格划分
        analy_line = line.split()
        if analy_line[-1] == 'rd':
            address_list.append(analy_line[0])
            # bit_list.append(analy_line[3])
        else:
            pass
    f1.close()
    # 输出地址计算相关指令
    return address_list


# 获取所有的循环指令
def get_loop_list():
    loop_list = ['59', '64', '147', '149']
    return loop_list


# 获取所有的分支指令
def get_bra_list():
    bra_list = ['38', '39', '40']
    return bra_list


# 获取所有比较指令
def cmp_list():
    # ins.txt
    f1 = open(file2, 'r')
    cmp_list = []
    for line in f1.readlines():
        analy_line = line.split()
        # 是分支指令
        if analy_line[1] == '@':
            # 加入影响分支指令的行
            cmp_list.append(str(int(analy_line[0]) - 1))
        else:
            pass
    f1.close()
    return cmp_list


# 获取所有存储指令
def get_store():
    f = open(file2, 'r')
    store_list = []
    store_bit = []
    for line in f.readlines():
        analy_line = line.split()
        if analy_line[1] == 'st':
            store_list.append(analy_line[0])
            store_bit.append(analy_line[3])
        else:
            pass
    f.close()
    # return store_list, store_bit
    return store_list


# 获取所有的加法
def get_add_list():
    f1 = open(file2, 'r')
    add_list = []
    for line in f1.readlines():
        analy_line = line.split()
        # if analy_line[1] == 'add' and analy_line[-1] != 'rd':
        if analy_line[1] == 'add':
            add_list.append(analy_line[0])
    f1.close()
    return add_list


# 获取所有的乘法
def get_mul_list():
    # ins.txt
    f1 = open(file2, 'r')
    cmul_list = get_constant_mul()
    mul_list = []
    for line in f1.readlines():
        analy_line = line.split()
        if analy_line[1] == 'mul' and analy_line[-1] != 'rd':
            if analy_line[0] not in cmul_list:
                mul_list.append(analy_line[0])
            else:
                pass

    f1.close()
    return mul_list


# 判断指令是否在循环内，并提取循环深度,不会提取【手动】
def in_loop(target_ins):
    ins_int = int(target_ins)
    if 59 <= ins_int <= 148:
        return '1'
    else:
        return '0'


# 获取常量乘法
def get_constant_mul():
    f1 = open("ins2.txt", 'r')
    mul_list = []
    for line in f1.readlines():
        analy_line = line.split()
        if analy_line[1].split('.')[0] == 'mul':
            if re.sub("[^a-z]", "", analy_line[2]) != 'rd':
                op = analy_line[-1].split(';')[0]
                if not op.startswith('%'):
                    mul_list.append(analy_line[0])
                else:
                    pass
    f1.close()
    return mul_list


# 获取所有指令影响的store个数
def get_all_store():
    f1 = open(file4, 'r')
    f2 = open("store_list", 'w')
    st_list, st_bit = get_store()
    for line in f1.readlines():
        analy_line = line.strip().split(',')
        influ_st_list = []
        for i in range(1, len(analy_line) - 1):
            if analy_line[i] in st_list:
                influ_st_list.append(analy_line[i])
            else:
                pass
        f2.write(analy_line[0] + ' ' + str(len(influ_st_list)) + '\n')
    f1.close()
    f2.close()


# 获取依赖特征
def influ_ins(target_ins):
    # dep_list.txt
    f1 = open(file4, 'r')
    # 1 mask
    # 1.1 mask指令列表
    mask_list = get_masked_ins()
    # 1.2 影响mask指令列表
    is_mask = False
    # 1.3 影响mask指令列表
    influ_mask_ins = []

    # 2 address
    # 2.1 地址指令列表
    address_list = address_ins()
    # 2.2 本身是否为地址指令
    is_address = False
    # 2.3 影响地址指令列表
    influ_address_list = []

    # 循环指令
    loop_list = get_loop_list()
    is_loop_ins = False
    influ_loop_list = []

    # 分支指令
    bra_list = get_bra_list()
    is_bra = False
    influ_bra_list = []

    # 4 存储指令
    # 4.1 存储指令列表
    st_list = get_store()
    # 4.2 本身为存储指令
    # 4.3 影响存储指令列表
    influ_st_list = []

    # 5 加法指令
    # 5.1 存储指令列表
    add_list = get_add_list()
    # 5.3 影响存储指令列表
    influ_add_list = []

    # 6 mul指令
    # 6.1 mul指令列表
    mul_list = get_mul_list()
    # 6.3 影响存储指令列表
    influ_mul_list = []

    # 6 mul指令
    # 6.1 mul指令列表
    cmul_list = get_constant_mul()
    # 6.3 影响存储指令列表
    influ_cmul_list = []

    # 5 影响的指令数
    influ_ins_num = 0

    for line in f1.readlines():
        analy_line = line.strip().split(',')
        # line number
        if analy_line[0] == target_ins:
            # 指令本身类型
            if target_ins in mask_list:
                is_mask = True
            else:
                is_mask = False

            if target_ins in address_list:
                is_address = True
            else:
                is_address = False

            if target_ins in loop_list:
                is_loop_ins = True
            else:
                is_loop_ins = False

            if target_ins in bra_list:
                is_bra = True
            else:
                is_bra = False

            influ_ins_num = len(analy_line) - 1
            for i in range(1, len(analy_line)):
                if analy_line[i] in address_list:
                    influ_address_list.append(analy_line[i])
                elif analy_line[i] in loop_list:
                    influ_loop_list.append(analy_line[i])
                elif analy_line[i] in bra_list:
                    influ_bra_list.append(analy_line[i])
                elif analy_line[i] in st_list:
                    influ_st_list.append(analy_line[i])
                elif analy_line[i] in mask_list:
                    influ_mask_ins.append(analy_line[i])
                elif analy_line[i] in add_list:
                    influ_add_list.append(analy_line[i])
                elif analy_line[i] in mul_list:
                    influ_mul_list.append(analy_line[i])
                elif analy_line[i] in cmul_list:
                    influ_cmul_list.append(analy_line[i])
        else:
            pass
    f1.close()
    s = ""
    # 1
    if is_mask:
        s += '1,'
    else:
        s += '0,'
    # 2
    if is_address:
        s += '1,'
    else:
        s += '0,'
    # 3
    if is_loop_ins:
        s += '1,'
    else:
        s += '0,'
    # 4
    if is_bra:
        s += '1,'
    else:
        s += '0,'
    # 5 影响的mask指令数
    s += str(len(influ_mask_ins)) + ','
    # 6 影响的addres指令数
    s += str(len(influ_address_list)) + ','
    # 7 是否影响循环指令
    if len(influ_loop_list) != 0:
        s += '1,'
    else:
        s += '0,'
    # 8 是否影响分支指令
    if len(influ_bra_list) != 0:
        s += '1,'
    else:
        s += '0,'
    # 9 影响的st指令数
    s += str(len(influ_st_list)) + ','
    # 10 影响的add指令数
    s += str(len(influ_add_list)) + ','
    # 11 影响的指令数
    s += str(influ_ins_num) + ','
    # 12 影响的常量乘法数
    s += str(len(influ_cmul_list)) + ','
    # 13 影响的普通mul指令数
    s += str(len(influ_mul_list))

    return s


# 获取有行号的特征
# 输入：con_result.txt 行号，统计SDC脆弱性
# 输出：all_feature.txt 行号，特征
def get_line_feature():
    # con_result.txt
    f1 = open(file7, 'r')
    # line_feature**.data
    f2 = open(file8, 'w')

    for line in f1.readlines():
        analy_line = line.strip().split()
        line_num = analy_line[0]
        sdc_rate = analy_line[1]

        # 依赖特征
        flow_feature = influ_ins(line_num)
        # 指令本身特征
        ins_fea = ins_feature(line_num)
        feature_list = flow_feature + "," + ins_fea
        if float(sdc_rate) >= 0.53:
            sdc_label = '1'
        else:
            sdc_label = '0'
        f2.write(line_num + ',' + feature_list + ',' + sdc_label + '\n')
        # f2.write(feature_list + '\n')
        # f3.write(sdc_label + '\n')
    f1.close()
    f2.close()


# 获取所有特征
# 输入：con_result.txt 行号，统计SDC脆弱性
# 输出：all_feature.txt 行号，特征
def get_all_feature():
    # con_result.txt
    f1 = open(file7, 'r')
    # all_feature**.data
    f2 = open(file5, 'w')
    
    for line in f1.readlines():
        analy_line = line.strip().split()
        print(analy_line)
        line_num = analy_line[0]
        sdc_rate = analy_line[1]

        # 依赖特征
        flow_feature = influ_ins(line_num)
        # 指令本身特征
        ins_fea = ins_feature(line_num)
        feature_list = flow_feature + "," + ins_fea
        if float(sdc_rate) >= 0.53:
            sdc_label = '1'
        else:
            sdc_label = '0'
        f2.write(feature_list + ',' + sdc_label + '\n')

    f1.close()
    f2.close()


dep_list_processed_file="dep_list_processed.txt"
all_features_file="all_features.txt"
result_file="result_test.txt"

def get_all_features():
    # con_result.txt
    f1 = open(result_file, 'r')
    # line_feature**.data
    f2 = open(all_features_file, 'w')
    for line in f1.readlines():
        analy_line = line.strip().split(',')
        # print(analy_line)
        itera_time = analy_line[0]
        app_name = analy_line[1]
        kernel_name = analy_line[2]###############kernel号1
        target_x = analy_line[3]
        target_y = analy_line[4]
        bit = analy_line[5]#######################哪一位发生了位翻转2
        fault_value = analy_line[6]
        target_line = analy_line[7] #提取这一行的依赖关系 13维
        ins_opcode = analy_line[8]#######################操作数类型3
        reg_digit = analy_line[9]#######################寄存器位数4
        reg_type = analy_line[10]#######################寄存器类型5
        des_reg = analy_line[11]#######################目的寄存器类型6
        ran_loop = analy_line[12]#######################循环轮数7
        exetime = analy_line[13]
        reverse = analy_line[14]#######################翻转方向8
        thelabel = analy_line[15]
        rate = analy_line[16]
        features=""

        # 特征1
        if kernel_name.startswith("_Z10std_kernelPfS_S_Pd"):
            features = features + "1,"
        elif kernel_name.startswith("_Z11corr_kernelPfS_Pd"):
            features = features + "2,"
        elif kernel_name.startswith("_Z11mean_kernelPfS_Pd"):
            features = features + "3,"
        elif kernel_name.startswith("_Z13reduce_kernelPfS_S_Pd"):
            features = features + "4,"
        else:
            features = features + "100,"
        
        # 特征2 3 4
        # features = features + target_x + "," + target_y + "," + bit + ","
        # print(bit)
        features = features + bit + ","
        

        #特征5 ins_opcode
        if ins_opcode == "add":
            features = features + "1,"
        elif ins_opcode == "and":
            features = features + "2,"
        elif ins_opcode == "cvta":
            features = features + "3,"
        elif ins_opcode == "fma":
            features = features + "4,"
        elif ins_opcode == "ld":
            features = features + "5,"
        elif ins_opcode == "mad":
            features = features + "6,"
        elif ins_opcode == "mov":
            features = features + "7,"
        elif ins_opcode == "mul":
            features = features + "8,"
        elif ins_opcode == "setp":
            features = features + "9,"
        elif ins_opcode == "shl":
            features = features + "10,"
        elif ins_opcode == "cvt":
            features = features + "11,"
        elif ins_opcode == "div":
            features = features + "12,"
        elif ins_opcode == "sqrt":
            features = features + "13,"
        elif ins_opcode == "sub":
            features = features + "14,"
        else :
            features = features + "100,"
        # print(features)
        #特征6 reg_digit
        features = features + reg_digit + ","

        #特征7 reg_type
        if reg_type == "b":
            features = features + "1,"
        elif reg_type == "f":
            features = features + "2,"
        elif reg_type == "pred":
            features = features + "3,"
        elif reg_type == "s":
            features = features + "4,"
        elif reg_type == "u":
            features = features + "5,"
        else: features = features + "100,"
        # print(features)
        #特征8 des_reg
        des_reg=des_reg[1:]
        if des_reg.startswith("f"):
            features = features + "1,"
        elif des_reg.startswith("p"):
            features = features + "2,"
        elif des_reg.startswith("r"):
            if des_reg[1]!="d":
                features = features + "3,"
            else:
                features = features + "4,"
        else: features = features + "100,"

        #特征9 ran_loop
        features = features + ran_loop + ","

        #特征10 reverse
        features = features + reverse + ","

        # #特征11 rate
        # features = features + rate + ","
        # print(features)

        #依赖特征
        flow_feature = influ_ins(target_line)
        # print(target_line)
        # print(flow_feature)
        # print(type(flow_feature))
        features = features + flow_feature + ","
        
        #标签
        if thelabel=="DUE":
            features = features + "1"
        if thelabel=="Masked":
            features = features + "2"
        if thelabel.startswith("SDC"):
            features = features + "3"
        # print(features)
        print(len(features.split(',')))
        f2.write(features)
        f2.write('\n')
        # f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}".format(itera_time, app_name, kernel_name, target_x,
        #                                                                  target_y, bit, fault_value, target_line,
        #                                                                  ins_opcode, reg_digit, reg_type, des_reg,ran_loop))
        
        # sdc_rate = analy_line[1]

        # # 依赖特征
        # flow_feature = influ_ins(line_num)
        # # 指令本身特征
        # ins_fea = ins_feature(line_num)
        # feature_list = flow_feature + "," + ins_fea
        # if float(sdc_rate) >= 0.53:
        #     sdc_label = '1'
        # else:
        #     sdc_label = '0'
        # f2.write(line_num + ',' + feature_list + ',' + sdc_label + '\n')
        # # f2.write(feature_list + '\n')
        # # f3.write(sdc_label + '\n')
        
    f1.close()
    f2.close()


def main():
    # 1 生成file2 ins.txt
    get_ins()
    # # 2 生成file6 ins2.txt
    get_ins2()
    # # 3 生成ins_feature.txt
    # get_ins_feature()
    # 4 生成flow_feature.txt
    # get_all_feature()
    # get_line_feature()

    get_all_features()


if __name__ == "__main__":
    main()
