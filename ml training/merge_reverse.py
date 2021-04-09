with open('basic.txt','r') as f1:
    with open('reverse.txt','r') as f2:
        with open('basic_reverse.txt','a') as f3:
            while True:# line1 <- line2
                lines1=f1.readlines()
                lines2=f2.readlines()

                if len(lines1)==0:
                    break
                # print(lines1)
                num=1
                for item1 in lines1:
                    item1=item1.strip('\n')
                    item1=item1+','+lines2[num]
                    num=num+2
                    f3.write(item1)