from flask import Flask, request, jsonify , render_template, request , url_for , redirect
import requests
import traceback
import logging
import os
import pickle
import  numpy as np
import sys
import tkinter
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
import json
from sklearn.model_selection import train_test_split, cross_val_score
import pickle
import psycopg2
import pandas as pd
from sklearn.metrics import mean_squared_error as mse
from flask_apscheduler import APScheduler
from predict.predict import predict
from training.training import training
from time import sleep

app = Flask(__name__)

scheduler = APScheduler() #BackgroundScheduler()
scheduler2 = APScheduler() #BackgroundScheduler()
scheduler3 = APScheduler()
scheduler4 = APScheduler() #BackgroundScheduler()
scheduler5 = APScheduler()


job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

app.register_blueprint(predict, url_prefix = "/predict")
app.register_blueprint(training, url_prefix = "/training")

@app.route("/index")
@app.route("/")
def index():

    return "Hello Welcome to Prediction Model API"



def traininglg():
    try:
        env_var = os.environ
        PG_HOST = env_var['PG_HOST']
        PG_USR = env_var['PG_USR']
        PG_PWD = env_var['PG_PWD']
        PG_DB = env_var['PG_DBB']

        conn = psycopg2.connect(dbname=PG_DB, user=PG_USR, host=PG_HOST, password=PG_PWD)
        cur = conn.cursor()
        data = pd.read_sql_query('''select region , depot ,item_no , avg(tms) as tms, avg(tms)/2 as ams ,  extract(month from creation_date) as month , 
        extract(year from creation_date) as year
        from lg_stock where date(creation_date) > (current_date - INTERVAL '11 month')
        group by region , depot ,item_no , month , year
        order by region, depot, item_no , year , month  
         ''', con=conn)

        dff = data.drop(['region', 'tms'], axis=1)

        dff['Sale_1Monthsback'] = 1
        dff['Sale_2Monthsback'] = 2
        dff['Sale_3Monthsback'] = 3
        print(dff.head(2))

        for y in dff['depot'].unique():
            for x in dff['item_no'].unique():
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_1Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+1)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_2Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+2)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_3Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+3)

        dff = dff.dropna()
        data = dff

        category_col = ['depot', 'item_no']
        labelEncoder = LabelEncoder()

        mapping_dict = {}
        for col in category_col:
            data[col] = labelEncoder.fit_transform(data[col])

            le_name_mapping = dict(zip(labelEncoder.classes_,
                                       labelEncoder.transform(labelEncoder.classes_)))

            mapping_dict[col] = le_name_mapping
        print(mapping_dict)

        y = data['ams']
        X = data.drop('ams', axis=1)

        print('X :', X.head())

        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        Xn = sc.fit_transform(X)
        Yn = y

        # Train and test split

        train_X, test_X, train_y, test_y = train_test_split(X, Yn, test_size=0.2, random_state=101)

        lr = LinearRegression()
        model2 = lr.fit(train_X, train_y)
        ypred = lr.predict(test_X)
        rmse1 = mse(test_y, ypred) ** (1 / 2)
        lrscore = cross_val_score(lr, train_X, train_y, cv=5)

        print('linear Regression RMSE: ', round(rmse1, 3),
              'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))

        mapp = str(mapping_dict)
        file = open('mapping_dict.txt', 'w')
        file.write(mapp)
        file.close()

        filename = 'lg_model.sav'
        pickle.dump(model2, open(filename, 'wb'))

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    # return (
    # 'linear Regression RMSE LG : ', round(rmse1, 3), 'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))


def trainingsw():
    try:
        env_var = os.environ
        PG_HOST = env_var['PG_HOST']
        PG_USR = env_var['PG_USR']
        PG_PWD = env_var['PG_PWD']
        PG_DB = env_var['PG_DBB']

        conn = psycopg2.connect(dbname=PG_DB, user=PG_USR, host=PG_HOST, password=PG_PWD)
        cur = conn.cursor()
        data = pd.read_sql_query('''select region , depot ,item_no , avg(tms) as tms, avg(tms)/2 as ams ,  extract(month from creation_date) as month , 
        extract(year from creation_date) as year
        from sw_stock where date(creation_date) > (current_date - INTERVAL '11 month')
        group by region , depot ,item_no , month , year
        order by region, depot, item_no , year , month  
         ''', con=conn)

        dff = data.drop(['region', 'tms'], axis=1)

        dff['Sale_1Monthsback'] = 1
        dff['Sale_2Monthsback'] = 2
        dff['Sale_3Monthsback'] = 3
        print(dff.head(2))

        for y in dff['depot'].unique():
            for x in dff['item_no'].unique():
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_1Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+1)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_2Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+2)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_3Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+3)

        dff = dff.dropna()
        data = dff

        category_col = ['depot', 'item_no']
        labelEncoder = LabelEncoder()

        mapping_dict = {}
        for col in category_col:
            data[col] = labelEncoder.fit_transform(data[col])

            le_name_mapping = dict(zip(labelEncoder.classes_,
                                       labelEncoder.transform(labelEncoder.classes_)))

            mapping_dict[col] = le_name_mapping
        print(mapping_dict)

        y = data['ams']
        X = data.drop('ams', axis=1)

        print('X :', X.head())

        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        Xn = sc.fit_transform(X)
        Yn = y

        # Train and test split

        train_X, test_X, train_y, test_y = train_test_split(X, Yn, test_size=0.2, random_state=101)

        lr = LinearRegression()
        model2 = lr.fit(train_X, train_y)
        ypred = lr.predict(test_X)
        rmse1 = mse(test_y, ypred) ** (1 / 2)
        lrscore = cross_val_score(lr, train_X, train_y, cv=5)

        print('linear Regression RMSE: ', round(rmse1, 3),
              'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))

        mapp = str(mapping_dict)
        file = open('mapping_dict_sw.txt', 'w')
        file.write(mapp)
        file.close()

        filename = 'sw_model.sav'
        pickle.dump(model2, open(filename, 'wb'))

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    # return (
    # 'linear Regression RMSE SW: ', round(rmse1, 3), 'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))




def trainingse():
    try:
        env_var = os.environ
        PG_HOST = env_var['PG_HOST']
        PG_USR = env_var['PG_USR']
        PG_PWD = env_var['PG_PWD']
        PG_DB = env_var['PG_DBB']

        conn = psycopg2.connect(dbname=PG_DB, user=PG_USR, host=PG_HOST, password=PG_PWD)
        cur = conn.cursor()
        data = pd.read_sql_query('''select region , depot ,item_no , avg(tms) as tms, avg(tms)/2 as ams ,  extract(month from creation_date) as month , 
        extract(year from creation_date) as year
        from se_stock where date(creation_date) > (current_date - INTERVAL '11 month')
        group by region , depot ,item_no , month , year
        order by region, depot, item_no , year , month  
         ''', con=conn)

        dff = data.drop(['region', 'tms'], axis=1)

        dff['Sale_1Monthsback'] = 1
        dff['Sale_2Monthsback'] = 2
        dff['Sale_3Monthsback'] = 3
        print(dff.head(2))

        for y in dff['depot'].unique():
            for x in dff['item_no'].unique():
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_1Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+1)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_2Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+2)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_3Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+3)

        dff = dff.dropna()
        data = dff

        category_col = ['depot', 'item_no']
        labelEncoder = LabelEncoder()

        mapping_dict = {}
        for col in category_col:
            data[col] = labelEncoder.fit_transform(data[col])

            le_name_mapping = dict(zip(labelEncoder.classes_,
                                       labelEncoder.transform(labelEncoder.classes_)))

            mapping_dict[col] = le_name_mapping
        print(mapping_dict)

        y = data['ams']
        X = data.drop('ams', axis=1)

        print('X :', X.head())

        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        Xn = sc.fit_transform(X)
        Yn = y

        # Train and test split

        train_X, test_X, train_y, test_y = train_test_split(X, Yn, test_size=0.2, random_state=101)

        lr = LinearRegression()
        model2 = lr.fit(train_X, train_y)
        ypred = lr.predict(test_X)
        rmse1 = mse(test_y, ypred) ** (1 / 2)
        lrscore = cross_val_score(lr, train_X, train_y, cv=5)

        print('linear Regression RMSE: ', round(rmse1, 3),
              'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))

        mapp = str(mapping_dict)
        file = open('mapping_dict_se.txt', 'w')
        file.write(mapp)
        file.close()

        filename = 'se_model.sav'
        pickle.dump(model2, open(filename, 'wb'))

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    # return (
    # 'linear Regression RMSE SE : ', round(rmse1, 3), 'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))



def trainingmb():
    try:
        env_var = os.environ
        PG_HOST = env_var['PG_HOST']
        PG_USR = env_var['PG_USR']
        PG_PWD = env_var['PG_PWD']
        PG_DB = env_var['PG_DBB']

        conn = psycopg2.connect(dbname=PG_DB, user=PG_USR, host=PG_HOST, password=PG_PWD)
        cur = conn.cursor()
        data = pd.read_sql_query('''select region , depot ,item_no , avg(tms) as tms, avg(tms)/2 as ams ,  extract(month from creation_date) as month , 
        extract(year from creation_date) as year
        from mb_stock where date(creation_date) > (current_date - INTERVAL '11 month')
        group by region , depot ,item_no , month , year
        order by region, depot, item_no , year , month  
         ''', con=conn)

        dff = data.drop(['region', 'tms'], axis=1)

        dff['Sale_1Monthsback'] = 1
        dff['Sale_2Monthsback'] = 2
        dff['Sale_3Monthsback'] = 3
        print(dff.head(2))

        for y in dff['depot'].unique():
            for x in dff['item_no'].unique():
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_1Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+1)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_2Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+2)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_3Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+3)

        dff = dff.dropna()
        data = dff

        category_col = ['depot', 'item_no']
        labelEncoder = LabelEncoder()

        mapping_dict = {}
        for col in category_col:
            data[col] = labelEncoder.fit_transform(data[col])

            le_name_mapping = dict(zip(labelEncoder.classes_,
                                       labelEncoder.transform(labelEncoder.classes_)))

            mapping_dict[col] = le_name_mapping
        print(mapping_dict)

        y = data['ams']
        X = data.drop('ams', axis=1)

        print('X :', X.head())

        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        Xn = sc.fit_transform(X)
        Yn = y

        # Train and test split

        train_X, test_X, train_y, test_y = train_test_split(X, Yn, test_size=0.2, random_state=101)

        lr = LinearRegression()
        model2 = lr.fit(train_X, train_y)
        ypred = lr.predict(test_X)
        rmse1 = mse(test_y, ypred) ** (1 / 2)
        lrscore = cross_val_score(lr, train_X, train_y, cv=5)

        print('linear Regression RMSE: ', round(rmse1, 3),
              'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))

        mapp = str(mapping_dict)
        file = open('mapping_dict_mb.txt', 'w')
        file.write(mapp)
        file.close()

        filename = 'mb_model.sav'
        pickle.dump(model2, open(filename, 'wb'))

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    # return (
    # 'linear Regression RMSE MB: ', round(rmse1, 3), 'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))
    #


def trainingnt():
    try:
        env_var = os.environ
        PG_HOST = env_var['PG_HOST']
        PG_USR = env_var['PG_USR']
        PG_PWD = env_var['PG_PWD']
        PG_DB = env_var['PG_DBB']

        conn = psycopg2.connect(dbname=PG_DB, user=PG_USR, host=PG_HOST, password=PG_PWD)
        cur = conn.cursor()
        data = pd.read_sql_query('''select region , depot ,item_no , avg(tms) as tms, avg(tms)/2 as ams ,  extract(month from creation_date) as month , 
        extract(year from creation_date) as year
        from nt_stock where date(creation_date) > (current_date - INTERVAL '11 month')
        group by region , depot ,item_no , month , year
        order by region, depot, item_no , year , month  
         ''', con=conn)

        dff = data.drop(['region', 'tms'], axis=1)

        dff['Sale_1Monthsback'] = 1
        dff['Sale_2Monthsback'] = 2
        dff['Sale_3Monthsback'] = 3
        print(dff.head(2))

        for y in dff['depot'].unique():
            for x in dff['item_no'].unique():
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_1Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+1)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_2Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+2)
                dff.loc[(dff.item_no == x) & (dff.depot == y), 'Sale_3Monthsback'] = dff.loc[
                    (dff.item_no == x) & (dff.depot == y), 'ams'].shift(+3)

        dff = dff.dropna()
        data = dff

        category_col = ['depot', 'item_no']
        labelEncoder = LabelEncoder()

        mapping_dict = {}
        for col in category_col:
            data[col] = labelEncoder.fit_transform(data[col])

            le_name_mapping = dict(zip(labelEncoder.classes_,
                                       labelEncoder.transform(labelEncoder.classes_)))

            mapping_dict[col] = le_name_mapping
        print(mapping_dict)

        y = data['ams']
        X = data.drop('ams', axis=1)

        print('X :', X.head())

        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        Xn = sc.fit_transform(X)
        Yn = y

        # Train and test split

        train_X, test_X, train_y, test_y = train_test_split(X, Yn, test_size=0.2, random_state=101)

        lr = LinearRegression()
        model2 = lr.fit(train_X, train_y)
        ypred = lr.predict(test_X)
        rmse1 = mse(test_y, ypred) ** (1 / 2)
        lrscore = cross_val_score(lr, train_X, train_y, cv=5)

        print('linear Regression RMSE: ', round(rmse1, 3),
              'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))

        mapp = str(mapping_dict)
        file = open('mapping_dict_nt.txt', 'w')
        file.write(mapp)
        file.close()

        filename = 'nt_model.sav'
        pickle.dump(model2, open(filename, 'wb'))

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    # return (
    # 'linear Regression RMSE: NT', round(rmse1, 3), 'Accuracy: %0.2f (+/- %0.2f)' % (lrscore.mean(), lrscore.std() * 2))
    #




if __name__  == '__main__' :
    scheduler.add_job(id='Scheduled task 1', func=traininglg, trigger='cron', year='*', month='*', day='last', hour=0, max_instances = 5)
    scheduler.start()
    scheduler2.add_job(id='Scheduled task 2', func=trainingsw, trigger='cron',  year='*', month='*', day='last', hour=0,  max_instances = 5)
    scheduler2.start()
    scheduler3.add_job(id='Scheduled task 3', func=trainingse, trigger='cron', year='*', month='*', day='last', hour=0,  max_instances = 5)
    scheduler3.start()
    scheduler4.add_job(id='Scheduled task 4', func=trainingmb, trigger='cron', year='*', month='*', day='last', hour=0,  max_instances = 5)
    scheduler4.start()
    scheduler5.add_job(id='Scheduled task 5', func=trainingnt, trigger='cron',  year='*', month='*', day='last', hour=0,  max_instances = 5)
    scheduler5.start()
    app.run(debug=True, host="0.0.0.0", port=5000)
    while True:
        sleep(20)


