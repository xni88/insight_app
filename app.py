from flask import Flask, render_template, request, send_file
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flask import request
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg')
from fbprophet import Prophet
import pickle

app = Flask(__name__)

# Python code to connect to Postgres
# You may need to modify this based on your OS, 
# as detailed in the postgres dev setup materials.

con = psycopg2.connect(dbname='d2difphsu953nk', host='ec2-50-19-95-77.compute-1.amazonaws.com', port=5432,
      user='juzjzvinglcfjp', password='c422d72e8217e6db42dab7d0d414a3283464294e7d3aae8e3d92d82964437a14', sslmode='require')

@app.route('/')
@app.route('/index')
def index():
    druglist=pd.read_csv('./static/data/druglist.csv')
    return render_template("input.html",druglist=druglist['Drugname'].tolist())

@app.route('/about')
def about():
   return render_template("about.html")

@app.route('/contact')
def contact():
   return render_template("contact.html")

@app.route('/db_fancy')
def druginventory_page_fancy():
   drug = int(request.args.get('NDCs'))
   sql_query = """
              SELECT "Dispensed_Item_NDC", "Dispensed_Medication", "Completed_Date", sum("DispensedQuantity") as ds, sum("Gross_Profit") as gp
              FROM test_drug_inventory_table
              WHERE "Dispensed_Item_NDC"='%s'
              GROUP BY "Dispensed_Item_NDC", "Dispensed_Medication", "Completed_Date"; 
               """ % drug

   query_results=pd.read_sql_query(sql_query,con)
   NDCs = []
   for i in range(0,query_results.shape[0]):
       NDCs.append(dict(Dispensed_Item_NDC=query_results.iloc[i]['Dispensed_Item_NDC'], Dispensed_Medication=query_results.iloc[i]['Dispensed_Medication'], Completed_Date=query_results.iloc[i]['Completed_Date'], DispensedQuantity=query_results.iloc[i]['ds'], Gross_Profit=query_results.iloc[i]['gp']))

   if drug == 35573040099: # Finasteride
      model = pickle.load(open("model_f.pickle", "rb"))
      forecast = pickle.load(open("forecast_f.pickle", "rb"))
      a = model.plot(forecast)
   elif drug == 378728353: # Noreth
      model = pickle.load(open("model_n.pickle", "rb"))
      forecast = pickle.load(open("forecast_n.pickle", "rb"))
      a = model.plot(forecast)
   elif drug == 61958070101: # Truvada
      model = pickle.load(open("model_t.pickle", "rb"))
      forecast = pickle.load(open("forecast_t.pickle", "rb"))
      a = model.plot(forecast)
   else:
      a = plt.plot()
      
   img = BytesIO()
   plt.savefig(img, format='png')
   img.seek(0)
   plt.clf()
   image = base64.b64encode(img.read()).decode('utf-8')

   return render_template('drug_inventory.html', NDCs=NDCs, image=image)


if __name__ == '__main__':
    app.run()