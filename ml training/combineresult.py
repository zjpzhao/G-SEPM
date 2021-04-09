# -*- coding: utf-8 -*-
# 本文件主要将basic和outcome合并，其中basic.txt和outcome.txt都是故障注入的输出结果
# 输入：basic.txt  outcome.txt
# 输出：result.txt

TIMENUM=3
# 生成38-149正向序列
def create_inslist():
    for i in range(38, 149):
        print(str(i) + ', ', end='')


# 倒序输出行号，依赖图
def reverse_linenum():
    f = open("1.txt", 'w')
    for i in range(149, 37, -1): # 左包含，右不包含
        f.write(str(i) + ',' + '\n')    
    f.close()


# 去除掉字符串中重复的字符，依赖图
def remove_repeat():
    # 去除字符串重复的元素
    str3 = '68,105,106,109,114,115,116,120,121,123,124,125,126,130,131,133,134,135,136,140,141,143,144,145,146,69,' \
           '70,73,74,75,76,80,81,83,84,85,86,90,91,93,94,95,96,66,104,105,106,109,114,115,116,119,124,125,126,129,134,' \
           '135,136,139,144,145,146,67,74,75,76,79,84,85,86,89,94,95,96,99'

    l_str = str3.split(',')
    l = list(set(l_str))
    l.sort()
    s = ''
    for item in l:
        s += ',' + item
    print(s)


def combine0():
    f1 = open("basic_reverse.txt", 'r+')
    f2 = open("outcome.txt", 'r')
    f3 = open("result_test.txt", 'w')
    mydict1 = {}
    for line in f2.readlines():
        analy_line = line.strip().split(',')
        line_num = analy_line[0]
        outcome_label = analy_line[1]
        sdc_rate = analy_line[2]
        if sdc_rate == "hang":
            reline = "DUE,1.0"
        elif sdc_rate == "nan":
            reline = "DUE,1.0"
        elif sdc_rate == "inf":
            reline = "DUE,1.0"
        elif str(sdc_rate) == "1.0":
            re_line = "DUE,1.0"
        elif float(sdc_rate) > 0.01:
            re_line = str("SDC_UNACCEPTABLE") + "," + str(sdc_rate)
        else:
            re_line = str(outcome_label)+","+str(sdc_rate)
        (key, value) = (line_num, re_line)
        mydict1[key] = value
        # print(mydict1)

    for line1 in f1.readlines():
        a_line1 = line1.split(',')
        line_num1 = a_line1[0]
        exetime = a_line1[-2][:-1]
        # print(exetime)
        if float(exetime) > 0.168*TIMENUM:
            v = "DUE,1.0"
        else :
            v = mydict1[line_num1]
        print(v)
        re_line1 = line1.strip(a_line1[0] + ',').split()
        v = str(re_line1) + "," + str(v)
        # print(v)
        mydict1[line_num1] = v
    # for line1 in f1.readlines():
    #     a_line1 = line1.split(',')
    #     line_num1 = a_line1[0]
    #     print(line_num1)
    #     re_line1 = line1.strip(a_line1[0] + ',').split()
    #     v = mydict1[line_num1]
    #     print(v)
    #     v = str(re_line1) + "," + str(v)
    #     mydict1[line_num1] = v

    

    for key in mydict1:
        s1 = str(key).replace("'", "")
        s2 = str(mydict1[key]).strip('[').strip(']').replace("'", "").replace("]", "").replace("[", ",")
        f3.write(s1 + ',' + s2 + '\n')

    f1.close()
    f2.close()
    f3.close()

# 合并basic和outcome，加入阈值
def combine(threshold):
    f1 = open("basic_reverse.txt", 'r+')
    f2 = open("outcome.txt", 'r')
    f3 = open("result09.txt", 'w')
    mydict1 = {}
    for line in f2.readlines():
        analy_line = line.strip().split(',')
        line_num = analy_line[0]
        outcome_label = analy_line[1]
        sdc_rate = analy_line[2]
        
        # 判断SDC率
        # if outcome_label == 'SDC' and float(real.txt.txt) == 1.0:
        #     re_line = ',DUE,100'
        # elif outcome_label == 'SDC' and float(real.txt.txt) >= float(threshold):
        #     # re_line = line.strip(analy_line[0] + ',').split()
        #     re_line = ',SDC,1'
        # elif outcome_label == 'SDC' and float(real.txt.txt) < float(threshold):
        #     re_line = str('Mask' + ',' + real.txt.txt).split()
        # elif outcome_label == 'SDC' and float(real.txt.txt) > 1.0:
        #     re_line = ',DUE,100'
        if float(sdc_rate) >= 1.0:
            re_line = "DUE,1.0"
        elif float(sdc_rate) < float(threshold):
            re_line = "IGSDC,1.0"
        else:
            re_line = str(outcome_label) + "," + str(sdc_rate)
        (key, value) = (line_num, re_line)
        mydict1[key] = value

    for line1 in f1.readlines():
        a_line1 = line1.split(',')
        line_num1 = a_line1[0]
        re_line1 = line1.strip(a_line1[0] + ',').split()
        v = mydict1[line_num1]
        print(v)

        v = str(re_line1) + "," + str(v)
        mydict1[line_num1] = v

    for key in mydict1:
        s1 = str(key).replace("'", "")
        s2 = str(mydict1[key]).strip('[').strip(']').replace("'", "").replace("]", "").replace("[", ",")
        f3.write(s1 + ',' + s2 + '\n')

    f1.close()
    f2.close()
    f3.close()

# 合并basic和outcome
def combine1():
    f1 = open("basic.txt", 'r+')
    f2 = open("outcome.txt", 'r')
    f3 = open("result0.txt", 'w')
    mydict1 = {}
    for line in f2.readlines():
        analy_line = line.strip().split(',')
		# 行号
        line_num = analy_line[0]
		# SDC，Masked，DUE
        outcome_label = analy_line[1]
		# metric
        sdc_rate = analy_line[2]
		# 如果metric超过1，就判定为DUE
        if float(sdc_rate) >= 1.0:
            re_line = "DUE,1.0"
        else:
            re_line = str(outcome_label) + "," + str(sdc_rate)
        (key, value) = (line_num, re_line)
		# 存储 结果标签，metric
        mydict1[key] = value

    for line1 in f1.readlines():
        a_line1 = line1.split(',')
		# 行号
        line_num1 = a_line1[0]
		# 除行号外的行
        re_line1 = line1.strip(a_line1[0] + ',').split()
        v = mydict1[line_num1]
        # 合并行号相同的行
        v = str(re_line1) + "," + str(v)
        mydict1[line_num1] = v

    for key in mydict1:
        s1 = str(key).replace("'", "")
        s2 = str(mydict1[key]).strip('[').strip(']').replace("'", "").replace("]", "").replace("[", ",")
		# 输出到result0.txt
        f3.write(s1 + ',' + s2 + '\n')

    f1.close()
    f2.close()
    f3.close()


def get_res(x):
    y = '{:.10f}'.format(x)  # .10f 保留10位小数
    return y


def main():
    # remove_repeat()
    # reverse_linenum()
    # combine0()
    combine0()
    # print(get_res(3.44E+07))
    # create_inslist()


if __name__ == "__main__":
    main()
