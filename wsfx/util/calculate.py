
#flag=1位事实，flag=2为结论
def calculatews(output,truedata, flag ):
    zip1 = zip(output,truedata)
    predict_true = 0
    predict_positive = 0
    true_positive = 0

    if flag == 1:
        for d1, d2 in zip1:
            if d1 > 0.3:
                if d2 == 1:
                    predict_true+= 1
                predict_positive += 1
            if d2 == 1:
                true_positive += 1

    if flag == 2:
        for d1, d2 in zip1:
            if d1 > 0.35:
                if d2 == 1:
                    predict_true+= 1
                predict_positive += 1
            if d2 == 1:
                true_positive += 1
    if predict_positive > 0 :
        precision =  predict_true/predict_positive
    else:
        precision = 0
    if true_positive > 0 :
        recall = predict_true/true_positive
    else:
        recall = -1

    return precision,recall
