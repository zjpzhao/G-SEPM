# -*- coding: utf-8 -*-
ptx_file = "correlation.ptx"
dryrun_before = "dryrun.out"
dryrun_file = "dryrun1.out"  # 删除多余内容后的文件
back_file = "correlation1.ptx"
temp_file = "temp.ptx"


# 删除dryrun.out多余行
def delete_line():
    f1 = open(dryrun_before, 'r')
    f2 = open(dryrun_file, 'w')

    i = 0
    for line in f1.readlines():
        if i < 25:
            i += 1
            continue
        i += 1
        line1 = line.strip('#$ ')
        f2.write(line1)
    f1.close()
    f2.close()


# 备份ptx文件
def back_ptx():
    f1 = open(ptx_file, 'r')
    f2 = open(back_file, 'w')

    for line in f1.readlines():
        f2.write(line)

    f1.close()
    f2.close()


# 读一个kernel的ptx，用于选择可以注错的指令
# 输出kernel数量，和label数量
def read_ptx():
    line_num = 0  # 行号
    f1 = open(back_file, 'r')
    f2 = open(temp_file, 'w')

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
        if analyze_line.startswith('@'):
            continue
        if analyze_line.startswith('ret'):
            continue
        # 分支指令没有目的寄存器，不分析
        if analyze_line.startswith('bra'):
            continue
        else:
            f2.write(str(line_num))  # 写入行号
            f2.write(" " + analyze_line + "\n")  # 写入指令行
    f1.close()
    f2.close()


def main():
    # 1 make keep and 2 make dry 之后
    # 3 删除dryrun多余的行，一次
    delete_line()
    print("Create dryrun1.out")
    # 4 备份，一次
    back_ptx()
    print("Backup ptx file")
    # 5 生成temp.ptx，多次错误注入只进行一次
    read_ptx()
    print("Create temp.ptx")


if __name__ == "__main__":
    main()
