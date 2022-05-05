from flask import request, jsonify , render_template, request , url_for , redirect
from flask import Blueprint

# from utils import
import os
import psycopg2
import pickle
import pandas as pd

predict = Blueprint('predict', __name__ , static_folder= "static", template_folder='templates')

@predict.route("/home", methods=["GET"])
@predict.route("/")
def base():


    return jsonify({"msgcode": 1, "status": "success", "message": "Welcome To Prediction System"}), 200


#http://127.0.0.1:5000/predict/lg?location=AGEGE&sku=PMF20HLK&c=11

@predict.route("/lg", methods=["GET"])
def lg():
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

        conn.commit()
        cur.close()
        conn.close()
    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    try:
        location = request.args.get('location')
        sku = request.args.get('sku')
        month = request.args.get('month')

        location = str(location)
        sku = str(sku)
        month = int(month)

        dff = data

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
        dff = dff.drop(['region', 'tms', 'ams'], axis=1)

        # location = 'AGEGE'
        # sku = '10040447'
        # month = 11

        abc = dff[(dff.item_no == sku) & (dff.depot == location) & (dff.month == month)]

        file1 = open("mapping_dict.txt")
        mapping_dict = file1.read()
        file1.close()
        mapping_dict = eval(mapping_dict)

        depot_ = mapping_dict['depot']
        item_no_ = mapping_dict['item_no']

        abc['depot'] = depot_[abc.depot.values[0]]
        abc['item_no'] = item_no_[abc.item_no.values[0]]
        print(abc)

        filename = 'lg_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        data = abc
        result = loaded_model.predict(data)

        if result > 0 :
            result = result
        else :
            result = 0
        print(result)

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    return str(result)


@predict.route("/sw", methods=["GET"])
def sw():
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

        conn.commit()
        cur.close()
        conn.close()
    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    try:
        location = request.args.get('location')
        sku = request.args.get('sku')
        month = request.args.get('month')

        location = str(location)
        sku = str(sku)
        month = int(month)

        dff = data

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
        dff = dff.drop(['region', 'tms', 'ams'], axis=1)


        abc = dff[(dff.item_no == sku) & (dff.depot == location) & (dff.month == month)]

        file1 = open("mapping_dict_sw.txt")
        mapping_dict = file1.read()
        file1.close()
        mapping_dict = eval(mapping_dict)

        depot_ = mapping_dict['depot']
        item_no_ = mapping_dict['item_no']

        abc['depot'] = depot_[abc.depot.values[0]]
        abc['item_no'] = item_no_[abc.item_no.values[0]]
        print(abc)

        filename = 'sw_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        data = abc
        result = loaded_model.predict(data)

        if result > 0 :
            result = result
        else :
            result = 0
        print(result)

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    return str(result)



@predict.route("/se", methods=["GET"])
def se():
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

        conn.commit()
        cur.close()
        conn.close()
    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    try:
        location = request.args.get('location')
        sku = request.args.get('sku')
        month = request.args.get('month')

        location = str(location)
        sku = str(sku)
        month = int(month)

        dff = data

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
        dff = dff.drop(['region', 'tms', 'ams'], axis=1)


        abc = dff[(dff.item_no == sku) & (dff.depot == location) & (dff.month == month)]

        file1 = open("mapping_dict_se.txt")
        mapping_dict = file1.read()
        file1.close()
        mapping_dict = eval(mapping_dict)

        depot_ = mapping_dict['depot']
        item_no_ = mapping_dict['item_no']

        abc['depot'] = depot_[abc.depot.values[0]]
        abc['item_no'] = item_no_[abc.item_no.values[0]]
        print(abc)

        filename = 'se_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        data = abc
        result = loaded_model.predict(data)

        if result > 0 :
            result = result
        else :
            result = 0

        print(result)

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    return str(result)


@predict.route("/mb", methods=["GET"])
def mb():
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

        conn.commit()
        cur.close()
        conn.close()
    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    try:
        location = request.args.get('location')
        sku = request.args.get('sku')
        month = request.args.get('month')

        location = str(location)
        sku = str(sku)
        month = int(month)

        dff = data

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
        dff = dff.drop(['region', 'tms', 'ams'], axis=1)


        abc = dff[(dff.item_no == sku) & (dff.depot == location) & (dff.month == month)]

        file1 = open("mapping_dict_mb.txt")
        mapping_dict = file1.read()
        file1.close()
        mapping_dict = eval(mapping_dict)

        depot_ = mapping_dict['depot']
        item_no_ = mapping_dict['item_no']

        abc['depot'] = depot_[abc.depot.values[0]]
        abc['item_no'] = item_no_[abc.item_no.values[0]]
        print(abc)

        filename = 'mb_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        data = abc
        result = loaded_model.predict(data)
        if result > 0 :
            result = result
        else :
            result = 0


        print(result)

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    return str(result)

@predict.route("/nt", methods=["GET"])
def nt():
    try:
        env_var = os.environ
        PG_HOST = env_var['PG_HOST']
        PG_USR = env_var['PG_USR']
        PG_PWD = env_var['PG_PWD']
        PG_DB= env_var['PG_DBB']

        conn = psycopg2.connect(dbname=PG_DB, user=PG_USR, host=PG_HOST, password=PG_PWD)
        cur = conn.cursor()
        data = pd.read_sql_query('''select region , depot ,item_no , avg(tms) as tms, avg(tms)/2 as ams ,  extract(month from creation_date) as month , 
        extract(year from creation_date) as year
        from nt_stock where date(creation_date) > (current_date - INTERVAL '11 month')
        group by region , depot ,item_no , month , year
        order by region, depot, item_no , year , month  
         ''', con=conn)

        conn.commit()
        cur.close()
        conn.close()
    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    try:
        location = request.args.get('location')
        sku = request.args.get('sku')
        month = request.args.get('month')

        location = str(location)
        sku = str(sku)
        month = int(month)

        dff = data

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
        dff = dff.drop(['region', 'tms', 'ams'], axis=1)


        abc = dff[(dff.item_no == sku) & (dff.depot == location) & (dff.month == month)]

        file1 = open("mapping_dict_nt.txt")
        mapping_dict = file1.read()
        file1.close()
        mapping_dict = eval(mapping_dict)

        depot_ = mapping_dict['depot']
        item_no_ = mapping_dict['item_no']

        abc['depot'] = depot_[abc.depot.values[0]]
        abc['item_no'] = item_no_[abc.item_no.values[0]]
        print(abc)

        filename = 'nt_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        data = abc
        result = loaded_model.predict(data)
        if result > 0 :
            result = result
        else :
            result = 0
        print(result)

    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    return str(result)


@predict.route("/jags", methods=["GET"])
def jags():
    try:
        env_var = os.environ
        PG_HOST = env_var['PG_HOST']
        PG_USR = env_var['PG_USR']
        PG_PWD = env_var['PG_PWD']
        PG_DB= env_var['PG_DBB']

        conn = psycopg2.connect(dbname=PG_DB, user=PG_USR, host=PG_HOST, password=PG_PWD)
        cur = conn.cursor()
        data = pd.read_sql_query('''select region , depot ,item_no , avg(tms) as tms, avg(tms)/2 as ams ,  extract(month from creation_date) as month ,
                extract(year from creation_date) as year
                from nt_stock where date(creation_date) > (current_date - INTERVAL '11 month')
                group by region , depot ,item_no , month , year
                order by region, depot, item_no , year , month
                 ''', con=conn)

        data1 = data.head()
        print(data1)
        print(PG_HOST)
        print(PG_USR)
        print(PG_PWD)
        print(PG_DB)




    except Exception as p:
        return jsonify({"error ": "... {}".format(p)})

    return str(PG_HOST)
