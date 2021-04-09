# -*- coding: utf-8 -*-
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report,accuracy_score,precision_score,recall_score,f1_score
from sklearn import metrics
from sklearn.utils import shuffle
from time import *
import numpy as np
import warnings
from sklearn.feature_selection import VarianceThreshold

from sklearn.model_selection import cross_val_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_gaussian_quantiles
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
warnings.filterwarnings("ignore")


file = 'all_features.txt' # 输入 带有行号的特征
file1 = "pre_label"	# 输出 预测标签
file2 = "result"		# 输出 结果
file3 = "test_data"	# 输出 测试数据
file4 = "test_label"	# 输出 测试标签
file5 = "train_data"	# 输出 训练数据
file6 = "train_label"	# 输出 训练标签

# DATADIM=5
random_state=9
train_size=0.8
test_size=0.2

train_data=[]
test_data=[]
train_label=[]
test_label=[]
def get_data():
    data = np.loadtxt(file, dtype=float, delimiter=',')
    # 划分特征值和特征标签------------------------修改---------------
    DATADIM=data.shape[1]-1
    print(DATADIM)
    x, y = np.split(data, indices_or_sections=(DATADIM,), axis=1)
    x,y=shuffle(x,y)
    # print(x.shape)
    # sel=VarianceThreshold(threshold=(.8 * (1 - .8)))
    # x=sel.fit_transform(x)
    # print(x.shape)
    
    # 划分训练数据集和测试数据集
    train_data, test_data, train_label, test_label = train_test_split(x, y, random_state = random_state, train_size=train_size,
                                                                      test_size=test_size)
    print(train_data)
    print(test_data)
    print(train_label)
    print(train_label)
    return train_data, test_data, train_label, test_label

# 训练模型
def train_model():
    train_data, test_data, train_label, test_label=get_data()
    best_score = 0
    for gamma in [0.001, 0.01, 0.1, 1, 10, 100]:
        for C in [0.001, 0.01, 0.1, 1, 10, 100]:
            svm1 = svm.SVC(gamma=gamma, C=C, kernel='rbf')  # 对于每种参数可能的组合，进行一次训练；
            svm1.fit(train_data, train_label)
            score = svm1.score(test_data, test_label)
            if score > best_score:  # 找到表现最好的参数
                best_score = score
                best_C = C
                best_gamma = gamma

    # 训练模型
    classifier = svm.SVC(C=best_C, kernel='rbf', gamma=best_gamma, decision_function_shape='ovr')

    classifier.fit(train_data, train_label.ravel())
    score = classifier.score(test_data,test_label)
    print('SVM score:',score)
    joblib.dump(classifier, 'svm.pkl') 
    return classifier, test_data, test_label, train_data, train_label

# 获得预测标签
def get_predict(classifier, test_data):
    predict_label = classifier.predict(test_data)
    return predict_label


# 获得auc
def get_auc(predict_label, test_label):
    auc = metrics.roc_auc_score(test_label, predict_label)
    return auc


# Accuracy
def get_accuracy(predict_label, test_label):
    # 预测标签
    # predict_label = classifier.predict(test_data)

    acc_score = accuracy_score(test_label, predict_label)
    return acc_score


# Precision
def get_precision(predict_label, test_label):
    # 预测标签
    # predict_label = classifier.predict(test_data)
    macro_precison = precision_score(test_label, predict_label, average='macro')
    micro_precision = precision_score(test_label, predict_label, average='micro')
    weigh_precision = precision_score(test_label, predict_label, average='weighted')
    precision = precision_score(test_label, predict_label, average=None)

    return macro_precison, micro_precision, weigh_precision


def get_recall(predict_label, test_label):
    # 预测标签
    # predict_label = classifier.predict(test_data)
    macro_recall = recall_score(test_label, predict_label, average='macro')
    micro_recall = recall_score(test_label, predict_label, average='micro')
    weigh_recall = recall_score(test_label, predict_label, average='weighted')
    # recall = recall_score(test_label, predict_label, average=None)

    return macro_recall, micro_recall, weigh_recall


def get_f1(predict_label, test_label):
    # 预测标签
    # predict_label = classifier.predict(test_data)
    macro_f1 = f1_score(test_label, predict_label, average='macro')
    micro_f1 = f1_score(test_label, predict_label, average='micro')
    weigh_f1 = f1_score(test_label, predict_label, average='weighted')
    # recall = recall_score(test_label, predict_label, average=None)

    return macro_f1, micro_f1, weigh_f1


def write_all_data(test_data, test_label, predict_label, train_data, train_label, filename):
    test_data_file=filename+"test_data_file.txt"
    test_label_file=filename+"test_label_file"
    predict_label_file=filename+"predict_label_file.txt"
    train_data_file=filename+"train_data.txt"
    train_label_file=filename+"train_label_file.txt"
    f1 = open(test_data_file, 'w')
    f2 = open(test_label_file, 'w')
    f3 = open(predict_label_file, 'w')
    f4 = open(train_data_file, 'w')
    f5 = open(train_label_file, 'w')

    np.savetxt(f1, test_data, fmt='%d', delimiter=',')
    np.savetxt(f2, test_label, fmt='%d', delimiter=',')
    np.savetxt(f3, predict_label, fmt='%d', delimiter=',')
    np.savetxt(f4, train_data, fmt='%d', delimiter=',')
    np.savetxt(f5, train_label, fmt='%d', delimiter=',')
    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()


def write_result(predict_label, test_label, time, filename):
    f = open(filename, 'w')
    f.write("Accuracy:" + str(get_accuracy(predict_label, test_label)) + "\n")
    f.write("Precision:" + str(get_precision(predict_label, test_label)) + "\n")
    f.write("recall:" + str(get_recall(predict_label, test_label)) + "\n")
    f.write("f1:" + str(get_f1(predict_label, test_label)) + "\n")
    # f.write("auc:" + str(get_auc(predict_label, test_label)) + "\n")
    f.write(time)
    f.close()



#adaboost
def train_ada_model():
    
    train_data, test_data, train_label, test_label=get_data()
    clf = AdaBoostClassifier(DecisionTreeClassifier(max_depth=10),n_estimators=100,learning_rate=1)#,algorithm="SAMME")
    clf.fit(train_data, train_label)
    # print(clf.feature_importances_)#模型的重要特征
    # y_pred = clf.predict(test_data)
    # print(classification_report(test_label, y_pred))
    # print()
    
    # print(accuracy_score(y_pred, test_label))
    score = clf.score(test_data,test_label)
    print('adaboost score:',score)
    
    joblib.dump(clf, 'ada.pkl')
    print(clf.feature_importances_)#模型的重要特征
    return clf, test_data, test_label, train_data, train_label
    # scores = cross_val_score(clf, train_data, train_label)
    # print(scores.mean())


def train_tree_model():
    train_data, test_data, train_label, test_label=get_data()
    #基尼
    clf = tree.DecisionTreeClassifier(criterion="entropy"
                                    ,random_state=30
                                    ,splitter='random'
                                    ,max_depth=10
                                    # ,min_samples_leaf=5
                                    # ,min_impurity_split=5
                                    )
    #信息熵
    # clf = tree.DecisionTreeClassifier(criterion="entropy")
    clf = clf.fit(train_data,train_label)
    score = clf.score(test_data,test_label)
    print('tree score:',score)
    
    joblib.dump(clf, 'tree.pkl') 
    print(clf.feature_importances_)#模型的重要特征
    # y_pred = clf.predict(test_data)
    # print(classification_report(test_label, y_pred))

    # feature_name = []

    # dot_data = tree.export_graphviz(clf
    #                                 ,out_file=None
    #                                 ,feature_names=feature_name
    #                                 ,class_names=[]
    #                                 ,filled=True
    #                                 ,rounded=True)
    # graph = graphviz.Source(dot_data)
    # graph.render('tree')
    return clf, test_data, test_label, train_data, train_label
def train_forest_model():
    train_data, test_data, train_label, test_label=get_data()
    clf = RandomForestClassifier(criterion='entropy')
    clf = RandomForestClassifier()
    clf.fit(train_data,train_label)

    score = clf.score(test_data,test_label)
    print('forest score:',score)
    joblib.dump(clf, 'forest.pkl') 
    print(clf.feature_importances_)#模型的重要特征
    return clf, test_data, test_label, train_data, train_label
    # predict_results=clf.predict(test_data)
    # print(accuracy_score(predict_results, test_label))
    # conf_mat = confusion_matrix(test_label, predict_results)
    # print(conf_mat)
    # print(classification_report(test_label, predict_results))

def main():
    # start_time = time()
    # classifier, test_data, test_label,train_data, train_label = train_model()
    # end_time = time()
    # predict_label = get_predict(classifier, test_data)
    # write_all_data(test_data, test_label, predict_label, train_data, train_label)
    # write_result(predict_label, test_label, str(end_time-start_time))


    # print("Accuracy:", get_accuracy(predict_label, test_label))
    # print("Precision:", get_precision(predict_label, test_label))
    # print("Recall:", get_recall(predict_label, test_label))
    # print("F1:", get_f1(predict_label, test_label))
    # print("Time:", end_time-start_time)
    get_data()
    # train_model()
    # train_ada_model()
    # train_tree_model()
    # train_forest_model()


    start_time = time()
    classifier, test_data, test_label,train_data, train_label = train_model()
    end_time = time()
    print("svm train time:{}".format(str(end_time-start_time)))

    predict_label = get_predict(classifier, test_data)
    write_all_data(test_data, test_label, predict_label, train_data, train_label,"SVM_")
    write_result(predict_label, test_label, str(end_time-start_time),"SVM_res.txt")


    
    start_time = time()
    classifier, test_data, test_label,train_data, train_label = train_ada_model()
    end_time = time()
    print("ada train time:{}".format(str(end_time-start_time)))

    predict_label = get_predict(classifier, test_data)
    write_all_data(test_data, test_label, predict_label, train_data, train_label,"ada_")
    write_result(predict_label, test_label, str(end_time-start_time),"ada_res.txt")
    
    start_time = time()
    classifier, test_data, test_label,train_data, train_label = train_tree_model()
    end_time = time()
    print("tree train time:{}".format(str(end_time-start_time)))

    predict_label = get_predict(classifier, test_data)
    write_all_data(test_data, test_label, predict_label, train_data, train_label,"tree_")
    write_result(predict_label, test_label, str(end_time-start_time),"tree_res.txt")

    start_time = time()
    classifier, test_data, test_label,train_data, train_label = train_forest_model()
    end_time = time()
    print("forest train time:{}".format(str(end_time-start_time)))
    predict_label = get_predict(classifier, test_data)
    write_all_data(test_data, test_label, predict_label, train_data, train_label,"forest_")
    write_result(predict_label, test_label, str(end_time-start_time),"forest_res.txt")

if __name__ == "__main__":
    main()
