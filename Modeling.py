#~~~~~~~~~~~~~~#
#Data Manipulation

#Getting Numerical Vars
def get_nums(data):
    #List of Numerical Features

    num_feats = []
    for feat in data.dtypes.index:
        if data[feat].dtype == "float64":
            num_feats.append(feat)
    return(num_feats)

#Encoding Numerical Vars
def scaling_nums(data, to_scale, train = True, train_data = None):
    std_scal = StandardScaler()
    #Label encoding when working with training data
    #When train = True, no need for train_data
    if train:
        data[to_scale] = std_scal.fit_transform(data[to_scale])
    #Since I want to fit the testing data based on the training data fit
    #Now need the train_data param
    else:
        std_scal.fit(train_data[to_scale])
        data[to_scale] = std_scal.transform(data[to_scale])
    return(data)

#Getting Categorical Vars
def get_cats(data):
    #List of Categorical Features

    cat_feats = []
    for feat in data.dtypes.index:
        if data[feat].dtype == "object":
            cat_feats.append(feat)
    return(cat_feats)

#Encoding Categorical Vars
def encoding_cats(data, train = True, train_data = None):
    #getting cat_feats
    cat_feats = get_cats(data)
    lab_encoder = LabelEncoder()
    #Label encoding when working with training data
    #When train = True, no need for train_data
    if train:
        for feat in cat_feats:
            encoded_col = "{}_encoded".format(feat)
            data[encoded_col] = lab_encoder.fit_transform(data[feat])
    #Since I want to fit the testing data based on the training data fit
    #Now need the train_data param
    else:
        for feat in cat_feats:
            encoded_col = "{}_encoded".format(feat)
            lab_encoder.fit(train_data[feat])
            data[encoded_col] = lab_encoder.transform(data[feat])
    data.drop(axis = 1, columns = cat_feats, inplace = True)
    return(data)

#Convert Region_code and District_code to Categorical
def to_category(data, to_cater):
    add_to_cater = get_cats(data)
    to_cater = to_cater.append(add_to_cater)
    for feat in to_cater:
        data[feat] = data[feat].astype('category')
    return(data)

#Dates

def as_dates(data):
    data.date_recorded = pd.to_datetime(data.date_recorded)
    return(data)

#~~~~~~~~~~~~~~#
#Modeling

#Validation Function:
#Adding random shuffle to cross validation folds

def rand_shuf_cv(train_data, target_data, model, n_folds):
    train_values = train_data.values
    y_train_values = target_data.values
    kfolds = KFold(n_folds, shuffle=True, random_state = 84)
    acc = np.sqrt(-cross_val_score(model, train_values, y_train_values, scoring = "accuracy", cv = kfolds))
    return(acc)

def modelfit(alg, dtrain, predictors, target, preformCV = True, cv_folds = 5, objective = "reg", print_feat_imp = False):

    """
    A Model fitting algorithm for sklearn models. The default setup is for regression tasks, but it also supportes
    functionality for classification as well. The objective is set to "reg" for the default regression, if you need
    classification, use objective = "class".
    Print_feat_imp is set to false by default, as it should only be run if the model has module .feature_importances.
    """

    #Fitting the algorithm on the data
    alg.fit(dtrain[predictors], dtrain[target])

    #Predicting Training Set
    dtrain_predictions = alg.predict(dtrain[predictors])
    if objective == "class":
        dtrain_predprob = alg.predict_proba(dtrain[predictors])[:,1]

    #Preforming Cross Validation
    if preformCV:
        from sklearn.model_selection import cross_val_score
        if objective == "reg":
            cv_score = cross_val_score(alg, dtrain[predictors], dtrain[target],
                                      cv = cv_folds, scoring="neg_mean_squared_error")
        elif objective == "class":
            cv_score = cross_val_score(alg, dtrain[predictors], dtrain[target],
                                      cv = cv_folds, scoring="accuracy")
        else:
            print("Invalid Objective")

    #Print Model Report:
    if objective == "reg":
        print("\nModel Report")
        print("Accuracy : {:4g}".format(metrics.mean_squared_error(dtrain[target].values, dtrain_predictions)))
        print("R^2 Score (Train): {}".format(metrics.r2_score(dtrain[target], dtrain_predictions)))
    elif objective == "class":
        print("\nModel Report")
        print("\tAccuracy : {:4g}".format(metrics.accuracy_score(dtrain[target].values, dtrain_predictions)))
        print("\tConfusion Matrix : \n{}".format(metrics.confusion_matrix(dtrain[target], dtrain_predictions)))

    if preformCV:
        print("\tCV Score: Mean = %.4g | Std = %.4g |\n \t\t Min = %.4g | Max = %.4g" % (np.mean(cv_score), np.std(cv_score), np.min(cv_score), np.max(cv_score)))

    #Plotting Feature Importances
    if print_feat_imp:
        fig = plt.figure(figsize = (15,10))
        feat_imp = pd.Series(alg.feature_importances_).sort_values(ascending = False)
        ax = feat_imp.plot(kind = "bar", title = "Feature Importances")
        plt.ylabel("Feature Importance Score")
        plt.xticks(rotation = "vertical")
        #The x ticks are shown as the col number by default
        #Here I revise this so they are listed by the feature name
        preds_dict = dict(zip(range(len(predictors)), predictors))
        x_labels = []
        for el in list(feat_imp.index):
            x_labels.append(preds_dict[el])
        plt.xticks(ticks = np.array(range(len(predictors))),
                  labels = x_labels)


def modelfit_xgb(alg, dtrain, predictors, target, useTrainCV = True, cv_folds = 5, early_stopping_rounds = 50, objective = 'reg', eval_metric = 'rmse'):

    """
    A Model fitting algorithm for the XGBoost algorithm, using the SKlearn wrapper. The default setup is for regression tasks, but it also supportes
    functionality for classification as well. The objective is set to "reg" for the default regression, if you need
    classification, use objective = "class".
    """

    if objective == 'class':
        le = LabelEncoder()
        dtrain[target] = le.fit_transform(dtrain[target])

    if useTrainCV:
        xgb_param = alg.get_xgb_params()
        #DMatrix is a data matrix used specifically for XGBoost
        #Optimized for both memory effiecncy and training speed
        xgtrain = xgb.DMatrix(dtrain[predictors].values,
                              label = dtrain[target].values)
        if objective == 'reg':
            cvresult = xgb.cv(xgb_param, xgtrain,
                               num_boost_round=alg.get_params()['n_estimators'],
                               nfold = cv_folds, metrics = "rmse",
                               early_stopping_rounds=early_stopping_rounds)
        if objective == 'class':
            cvresult = xgb.cv(xgb_param, xgtrain,
                               num_boost_round=XGB.get_params()['n_estimators'],
                               nfold = cv_folds, metrics = "merror",
                               early_stopping_rounds=early_stopping_rounds)

        alg.set_params(n_estimators = cvresult.shape[0])

    #Fitting the algorithm on the data
    alg.fit(dtrain[predictors], dtrain[target], eval_metric = eval_metric)

    #Predicting Training Set
    dtrain_predictions = alg.predict(dtrain[predictors])
    #dtrain_predprob = alg.predict_proba(dtrain[predictors])[:,1]

    #Print Model Report:
    if objective == 'reg':
        print("\nModel Report")
        print("Accuracy : {:4g}".format(metrics.mean_squared_error(dtrain[target].values, dtrain_predictions)))
        print("R^2 Score (Train): {}".format(metrics.r2_score(dtrain[target], dtrain_predictions)))

    elif objective == "class":
        print("\nModel Report")
        print("\tAccuracy : {:4g}".format(metrics.accuracy_score(dtrain[target].values, dtrain_predictions)))
        print("\tConfusion Matrix : \n{}".format(metrics.confusion_matrix(dtrain[target], dtrain_predictions)))

        print("\tCV Merror rate Training: Mean = %.4g | Std = %.4g \n \t\t Min = %.4g" % (np.mean(cvresult['train-merror-mean']), np.mean(cvresult['train-merror-std']), np.min(cvresult['train-merror-mean'])))
        print("\tCV Merror rate Testing: Mean = %.4g | Std = %.4g \n \t\t Min = %.4g" % (np.mean(cvresult['test-merror-mean']), np.mean(cvresult['test-merror-std']), np.min(cvresult['test-merror-mean'])))


    #Plotting Feature Importances
    fig = plt.figure(figsize = (15,10))
    feat_imp = pd.Series(alg.feature_importances_).sort_values(ascending = False)
    top_25 = feat_imp.iloc[:25]
    print(top_25)
    ax = top_25.plot(kind = "bar", title = "Feature Importances")
    plt.ylabel("Feature Importance Score")
    plt.xticks(rotation = "vertical")
    #The x ticks are shown as the col number by default
    #Here I revise this so they are listed by the feature name
    preds_dict = dict(zip(range(len(predictors)), predictors))
    x_labels = []
    for el in list(top_twenty.index):
        x_labels.append(preds_dict[el])
        prin(el)
    plt.xticks(ticks = np.array(range(25)),
              labels = x_labels)
    print(x_labels)
