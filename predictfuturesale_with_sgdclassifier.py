# -*- coding: utf-8 -*-
"""PredictFutureSale with SGDClassifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OQJp61ZFHE27oQ3P7XDhjOfkaQ2Aukxr
"""

# Commented out IPython magic to ensure Python compatibility.
import warnings
warnings.filterwarnings('ignore')

import math, time, datetime
from math import sqrt
import numpy as np 
import pandas as pd
# from scipy import stats

from matplotlib import pyplot as plt
import missingno as msno
# %matplotlib inline

from sklearn.model_selection import train_test_split, cross_val_score, cross_validate, cross_val_predict
from sklearn.metrics import (classification_report, confusion_matrix, roc_curve, roc_auc_score, 
                             precision_recall_curve, auc, log_loss, accuracy_score, f1_score, mean_squared_error)
from sklearn.feature_selection import (mutual_info_classif, SelectKBest, chi2, RFE, RFECV)

from sklearn.svm import LinearSVC
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression, LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier

df_first = pd.read_csv("sales_train.csv")
df_test_first = pd.read_csv("test.csv")
df_sample_sub = pd.read_csv("sample_submission.csv")
df_items = pd.read_csv("items.csv")
df_items_cat = pd.read_csv("item_categories.csv")
df_shops = pd.read_csv("shops.csv")

df_first.head()

df_test_first.head()

df_sample_sub.head()

df_items.head()

df_items_cat.head()

df_shops.head()

df_first.info()

## plot graphic of missing values
msno.matrix(df_first, figsize=(10, 4))

# Checking for missing values
df_first.isnull().sum()

df_dropped = df_first.drop(['date','item_price'], axis=1)
df_dropped.head()

df_forecast_dropped = df_test_first.drop(['ID'], axis=1)
df_forecast_dropped.head()

### It will zero variance features
from sklearn.feature_selection import VarianceThreshold
var_thres=VarianceThreshold(threshold=0)
var_thres.fit(df_dropped)
df_dropped.columns[var_thres.get_support()]

constant_columns = [column for column in df_dropped.columns
                    if column not in df_dropped.columns[var_thres.get_support()]]

print(len(constant_columns))

df_dropped = df_dropped.drop(constant_columns,axis=1)
df_dropped.head()

# There is no categorical columns in the dataframe
categorical_feature_columns = list(set(df_dropped.columns) - set(df_dropped._get_numeric_data().columns))
categorical_feature_columns

numerical_feature_columns = list(df_dropped._get_numeric_data().columns)
numerical_feature_columns

for col in df_dropped:
    unique_vals = np.unique(df_dropped[col])
    nr_values = len(unique_vals)
    if nr_values < 10:
        print(f'The number of values for feature {col} :{nr_values} -- {unique_vals}')
    else:
        print(f'The number of values for feature {col} :{nr_values}')

df_group = df_dropped.groupby(['date_block_num', 'shop_id', 'item_id']).sum().reset_index()
df_group.head()

df_train = df_group.pivot_table(index=['shop_id','item_id'], columns='date_block_num', values='item_cnt_day', 
                        fill_value=0)
df_train.reset_index(inplace=True)
df_train.head()

df_test = pd.merge(df_forecast_dropped, df_train, on=['shop_id','item_id'], how='left').fillna(0)
df_test.head()

X = df_train[df_train.columns[:-1]].values
y = df_train[df_train.columns[-1]]
print(X.shape)
print(y.shape)

# first one
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size = 0.8, test_size=0.15, random_state=15)

# Second one
X_train, X_valid, y_train, y_valid = train_test_split(X_train, y_train, train_size = 0.9, test_size=0.1, random_state=15)

print(X_train.shape)
print(X_test.shape)
print(X_valid.shape)

print(y_train.shape)
print(y_test.shape)
print(y_valid.shape)

SGDC_reg = SGDClassifier().fit(X_train, y_train)

# Accuracy on Validation
print('The Validation Accuracy is: {:.1%}'.format(SGDC_reg.score(X_valid, y_valid)))
print('The Validation MSE is: {:.8}'.format(mean_squared_error(y_valid, SGDC_reg.predict(X_valid))))

# Accuracy on Test
print('The Testing Accuracy is: {:.1%}'.format(SGDC_reg.score(X_test, y_test)))
print('The Testing MSE is: {:.8}'.format(mean_squared_error(y_test, SGDC_reg.predict(X_test))))

"""**Submission**"""

X_forecast = df_test[df_test.columns[:-1]].values
y_forecast_pred = SGDC_reg.predict(X_forecast)
y_forecast_pred = list(map(round, y_forecast_pred))

y_forecast_pred[:20]

# Create a submisison dataframe and append the relevant columns
submission = pd.DataFrame()
submission['ID'] = df_test_first['ID']
submission['item_cnt_month'] = y_forecast_pred # predictions on the test dataset
submission.head()

# Convert submisison dataframe to csv for submission to csv for Kaggle submisison
submission.to_csv('predict_future_sales.csv', index=False)
print('Submission CSV is ready!')

# Check the submission csv to make sure it's in the right format
submissions_check = pd.read_csv("predict_future_sales.csv")
submissions_check.head()