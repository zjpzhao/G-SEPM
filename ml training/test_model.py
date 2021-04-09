import joblib
import numpy as np
from time import *
from sklearn import svm
from sklearn.metrics import classification_report



def testmodel(modelname):
    DUE=0
    Masked=0
    SDC=0

    DUE_pre=0
    Masked_pre=0
    SDC_pre=0
    test_data_file = modelname + "_test_data_file.txt"
    test_label_file = modelname + "_test_label_file"
    # 导入测试集
    data = np.loadtxt(test_data_file, dtype=float, delimiter=',')
    label = np.loadtxt(test_label_file, dtype=float, delimiter=',')
    DATANUM=data.shape[0]
    print(DATANUM)
    # data = data[0:1]
    # label = label[0:1]
    # print(data)
    # print(label)
    # print(type(data))
    modelfile = modelname + ".pkl"
    clf = joblib.load(modelfile)
    pre_label=[]
    


    for i in range(DATANUM):
        # print(("["+str(data[i])+"]"))
        y_pred = clf.predict(data[i][None])
        # print('{0} {1}'.format(label[i], y_pred[0]))
        pre_label.append(y_pred[0])
    # print(label)
    # print("##################################################################################")
    # print(pre_label)
    
    result_directed = [[a,b] for a,b in zip(label,pre_label)]
    with open("result_directed.txt","w") as f:
        for i in result_directed:
            f.write(str(int(i[0]))+" "+str(int(i[1]))+"\n")
    # print(result_directed)
    target_names = ['DUE', 'Masked', 'SDC']  
    y_pred = clf.predict(data)
    print(classification_report(label, y_pred,target_names=target_names,digits=5))

    # 统计真值，三种类别 实际各有多少个
    for thelabel in label:
        if thelabel==1:
            DUE=DUE+1
        elif thelabel==2:
            Masked=Masked+1
        elif thelabel==3:
            SDC=SDC+1
        else: print("ERROR")

    #统计预测出来的三类各有多少个
    for prelabel in pre_label:
        if prelabel==1:
            DUE_pre=DUE_pre+1
        elif prelabel==2:
            Masked_pre=Masked_pre+1
        elif prelabel==3:
            SDC_pre=SDC_pre+1
        else: print("ERROR")


    print("True:")
    print(DUE)
    print(Masked)
    print(SDC)
    print("Pre:")
    print(DUE_pre)
    print(Masked_pre)
    print(SDC_pre)
    
    
    vital_label=label
    vital_pre_label=pre_label
    # print(type(vital_label))
    # print(type(vital_pre_label))

    for i in range(len(vital_label)):
        # print(type(vital_label[i]))
        if int(vital_label[i])==3:
            vital_label[i]=1

    for j in range(len(vital_pre_label)):
        # print(type(vital_pre_label[i]))
        if vital_pre_label[j]==3:
            vital_pre_label[j]=1
    vital_result_directed = [[a,b] for a,b in zip(vital_label,vital_pre_label)]
    # print(vital_result_directed)
    with open("vital.txt","w") as f:
        for i in vital_result_directed:
            f.write(str(int(i[0]))+" "+str(int(i[1]))+"\n")


    vital_target_names = ['Vital', 'Masked']
    print(classification_report(vital_label, vital_pre_label,target_names=vital_target_names,digits=5))
    
    
    



def main():
    start_time = time()
    testmodel("svm")
    end_time = time()
    print(str(end_time-start_time))

    start_time = time()
    testmodel("ada")
    end_time = time()
    print(str(end_time-start_time))

    start_time = time()
    testmodel("forest")
    end_time = time()
    print(str(end_time-start_time))

    start_time = time()
    testmodel("tree")
    end_time = time()
    print(str(end_time-start_time))



if __name__ == "__main__":
    main()