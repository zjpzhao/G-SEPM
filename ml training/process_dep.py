insert_line1 = 18
# # 处理依赖表
# def process_dep():
with open("dep_list.txt",'r') as fdep:
    with open("dep_list_processed.txt",'w') as fdeppro:
        line_list=[]
        new_line_list=""
        while True:
            line1=fdep.readline()        
            line1=line1.strip('\n')
            if len(line1)==0:
                break

            line_list=line1.split(',')
            # print(line_list)
            # print("_________________________________________________________")
            #遍历依赖表，加行
            for numoflist in range(len(line_list)):
                
                if int(line_list[numoflist]) >= insert_line1:
                    line_list[numoflist]=str(int(line_list[numoflist])+1)
                else : print("不变")
                # print(line_list[numoflist])
            # print(line_list)
            
            new_line_list=','.join(line_list)
            # print(new_line_list)
            fdeppro.write(new_line_list)
            fdeppro.write('\n')


