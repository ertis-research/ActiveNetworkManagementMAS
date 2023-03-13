from time import time
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.shortcuts import render,redirect
from django import forms

from django.views.generic import TemplateView
from sklearn import model_selection

import json
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pickle import load
import tensorflow as tf
import os
from . import models
from .models import classes
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.realpath('DataMonitoring/models/'))
 

from bson.json_util import dumps


from Crypto.Hash import HMAC, SHA256


#################################################################### MAIN CODE#############################################

host = os.environ.get("HOST")
user = os.environ.get("USER")
passw = os.environ.get("PASSW")
client = MongoClient(host=host, username=user, password=passw)
action_values = ["Do nothing", "Small change temperature", "Big Change temperature", "EV Charge", "EV Discharge", "SB Charge20", "SB Charge40" ,"SB Charge60", "SB Discharge20" ,"SB Discharge40", "SB Discharge60", "Small Change Temperature and EV Charge", "Small Change Temperature and EV Discharge", "Small Change Temperature and SB Charge20", "Small Change Temperature and SB Charge40", "Small Change Temperature and SB Charge60", "Small Change Temperature and SB Discharge20", "Small Change Temperature and SB Discharge40", "Small Change Temperature and SB Discharge60", "Big Change Temperature and EV Charge", "Big Change Temperature and EV Discharge", "Big Change Temperature and SB Charge20", "Big Change Temperature and SB Charge40", "#Big Change Temperature and SB Charge60", "Big Change Temperature and SB Discharge20", "Big Change Temperature and SB Discharge40", "Big Change Temperature and SB Discharge60", "EV Charge and SB Charge20", "EV Charge and SB Charge40", "EV Charge and SB Charge60", "EV Charge and SB Discharge20", "EV Charge and SB Discharge40", "EV Charge and SB Discharge60", "EV Discharge and SB Charge20", "EV Discharge and SB Charge40", "EV Discharge and SB Charge60", "EV Discharge and SB Discharge20", "EV Discharge and SB Discharge40", "EV Discharge and SB Discharge60", "Small Change Temperature, EV Charge and SB Charge20", "Small Change Temperature, EV Charge and SB Charge40", "Small Change Temperature, EV Charge and SB Charge60", "EV Charge and SB Discharge20", "Small Change Temperature, EV Charge and SB Discharge40", "Small Change Temperature, EV Charge and SB Discharge60", "Big Change Temperature, EV Charge and SB Charge20", "Big Change Temperature, EV Charge and SB Charge40", "Big Change Temperature, EV Charge and SB Charge60", "Big Change Temperature, EV Charge and SB Discharge20", "Big Change Temperature, EV Charge and SB Discharge40",  "Big Change Temperature, EV Charge and SB Discharge60"]
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Create your views here.

class LoginView(TemplateView):

    def get(self, request):
        return render(request, 'login.html')
    def post(self,request):
        login = LoginForm(request.POST or None)
        if request.method == "POST" and login.is_valid():
            user = login.cleaned_data["user"] if login.cleaned_data["user"] else None
            passw = login.cleaned_data["passw"] if login.cleaned_data["passw"] else None

            if user and passw != None:
                db = client.Ebalance
                col_p = db["Passwords"]
                h = HMAC.new(passw.encode("utf-8"), digestmod=SHA256)
                hash_val = h.update(user.encode("utf-8"))
                hash_hexa = hash_val.hexdigest()
                access = col_p.find({},{"user": user, "password" : hash_hexa}).sort("_id", -1).limit(1)
                if len(list(access)):
                    response =  redirect('index')
                    response.set_cookie('access', VALUE)
                    return response
                else:
                    return HttpResponseRedirect("login.html")
            else:
                return HttpResponseRedirect("login.html")


        
class HomeView(TemplateView):

    def get(self, request):
        cookie = request.COOKIES.get('access')
        now = datetime.timestamp(datetime.now())  
        if cookie != None:
            db = client.Ebalance
            col = db["emv210"]
            data = col.find({},{"datetime" : 1, "kwh_p_tot_r" : 1}).sort("_id", -1).limit(10) 
            url = "http://research.adabyron.uma.es:8046/d/ayXEGW-Vz/real-time-data?from"+str((1654509600)*1000)+"&to="+str(now*1000)+"&orgId=1"
            return render(request, 'index.html', {'data': data, "url" : url})
        else:
            return HttpResponseRedirect("Login")
    def post(self, request):
        return HttpResponseRedirect("Login")


class ErrorView(TemplateView):
    def get(self, request):
        cookie = request.COOKIES.get('access')
        now = datetime.timestamp(datetime.now())  
        if cookie != None:
            url = "http://research.adabyron.uma.es:8046/d/ayXEGW-Vz/real-time-data?orgId=1&from="+str((1654509600)*1000)+"&to="+str(now*1000)+"&viewPanel=4" 
            url1 = "http://research.adabyron.uma.es:8046/d/ayXEGW-Vz/real-time-data?orgId=1&from="+str((1654509600)*1000)+"&to="+str(now*1000)+"&refresh=15m&viewPanel=6" 
            url2 = "http://research.adabyron.uma.es:8046/d/ayXEGW-Vz/real-time-data?orgId=1&from="+str((1654509600)*1000)+"&to="+str(now*1000)+"&viewPanel=8" 
            url3 = "http://research.adabyron.uma.es:8046/d/ayXEGW-Vz/real-time-data?orgId=1&from="+str((1654509600)*1000)+"&to="+str(now*1000)+"&viewPanel=10" 
            return render(request, 'errors.html', {"url" : url, "url1" : url1, "url2" : url2, "url3" : url3})
        else:
            return HttpResponseRedirect("Login")
    def post(self, request):
        return HttpResponseRedirect("Login")

class ForecastingView(TemplateView):
    def get(self, request):
        cookie = request.COOKIES.get('access')
        if cookie != None:
            model_dense_500 = tf.keras.models.load_model("DataMonitoring/models/model_dense_500.h5")
            model_lstm_250 = tf.keras.models.load_model("DataMonitoring/models/model_lstm_250.h5")
            db = client.Ebalance
            col = db["emv210"]

            data = col.find({},{"datetime" : 1, "kwh_p_tot_r" : 1}).sort("_id", -1) 

            timestamp = pd.to_datetime(data[0]["datetime"])
            dow = timestamp.dayofweek
            timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            day = timestamp[0:2]
            month = timestamp[3:5]
            year = timestamp[6:10]
            hour = timestamp[11:13]
            minute = timestamp[14:16]
            d = datetime(int(year), int(month), int(day), int(hour), int(minute))
            curve = []

            db = client.Ebalance
            col2 = db["openweather"]
            data2 = col2.find().sort("_id", -1)
            scaler = load(open("DataMonitoring/models/cemosa-scaler-forecasting.pkl", 'rb'))
            for x in range(1,21):
                timestamp = pd.to_datetime(data[96-x]["datetime"])
                dow = timestamp.dayofweek
                timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                day = float(timestamp[0:2])
                month = float(timestamp[3:5])
                year = float(timestamp[6:10])
                hour = float(timestamp[11:13])
                minute = float(timestamp[14:16])
                d +=  timedelta(minutes=15)
                
                new_x = np.array([[data[96-x]["kwh_p_tot_r"], data2[96-x]["temp_min"] , data2[96-x]["temp_max"], data2[96-x]["humidity"], data2[96-x]["wind"], dow, month, hour, data[192-x]["kwh_p_tot_r"], data[288-x]["kwh_p_tot_r"], data[384-x]["kwh_p_tot_r"], data[480-x]["kwh_p_tot_r"], data[576-x]["kwh_p_tot_r"], data[672-x]["kwh_p_tot_r"], data[768-x]["kwh_p_tot_r"]]])
                X = scaler.transform(new_x)
                val1 = model_dense_500.predict(X)
                val2 = model_lstm_250.predict(X)
                val = (float(val1[0][0]) + float(val2[0][0]))/2
                curve.append({'datetime': d.strftime('%d/%m/%Y %H:%M:%S') , 'value':round(val,2)})

        

            return render(request, 'forecasting.html', {'data': curve})
        else:
            return HttpResponseRedirect("Login")
    def post(self, request):
        return HttpResponseRedirect("Login")


class ScenariosView(TemplateView):
    def get(self, request):
        cookie = request.COOKIES.get('access')
        now = datetime.timestamp(datetime.now())  
        if cookie != None:
            db = client.Ebalance
            col = db["emv210"]

            data = col.find({},{"datetime" : 1, "kwh_p_tot_r" : 1}).sort("_id", -1).limit(672) 

            timestamp = pd.to_datetime(data[0]["datetime"])
            dow = timestamp.dayofweek
            timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            day = timestamp[0:2]
            month = timestamp[3:5]
            year = timestamp[6:10]
            hour = timestamp[11:13]
            minute = timestamp[14:16]
            second = timestamp[17:19]
            
            
            col2 = db["openweather"]
            weather = 0
            data2 = col2.find().sort("_id", -1).limit(1)
            if data2[0]["weather"] == "Clouds":
                weather = 0
            elif data2[0]["weather"] == "Clear":
                weather = 1
            elif data2[0]["weather"] == "Rain":
                weather = 2
            elif data2[0]["weather"] == "Drizzle":
                weather = 3
            elif data2[0]["weather"] == "Mist":
                weather = 4
            elif data2[0]["weather"] == "Thunderstorm":
                weather = 5
            elif data2[0]["weather"] == "Haze":
                weather = 6
            elif data2[0]["weather"] == "Fog":
                weather = 7

            scaler = load(open("DataMonitoring/models/cemosa-scaler-4.pkl", 'rb'))

            model_lstm = tf.keras.models.load_model("DataMonitoring/models/lstm-cemosa-4.h5")
            new_x = np.array([[data[0]["kwh_p_tot_r"], weather, data2[0]["temp_min"] , data2[0]["temp_max"], data2[0]["pressure"], data2[0]["humidity"], data2[0]["wind"], day, month, year, hour, minute, second, dow,data[96]["kwh_p_tot_r"], data[192]["kwh_p_tot_r"], data[288]["kwh_p_tot_r"], data[384]["kwh_p_tot_r"], data[480]["kwh_p_tot_r"], data[576]["kwh_p_tot_r"], data[672]["kwh_p_tot_r"]]])
            X = scaler.transform(new_x)

            lstm_pred = model_lstm.predict(X)[0].tolist()
            curve = []
            d = datetime(int(year), int(month), int(day), int(hour), int(minute))


            for i, v in enumerate(lstm_pred):
                d +=  timedelta(minutes=15)
                curve.append({'datetime': d.strftime('%d/%m/%Y %H:%M:%S') , 'value':round(lstm_pred[i],2)})

            action_values = ["Do nothing.","Small change temperature","Big Change temperature ","Huge Change temperature","EV Charge","EV Discharge","SB Charge20","SB Charge40","SB Charge60","SB Discharge20","SB Discharge40","SB Discharge60","Small Change Temperature and EV Charge","Small Change Temperature and EV Discharge","Small Change Temperature and SB Charge20","Small Change Temperature and SB Charge40","Small Change Temperature and SB Charge20","Small Change Temperature and SB Discharge20","Small Change Temperature and SB Discharge40","Small Change Temperature and SB Discharge60","Big Change Temperature and EV Charge","Big Change Temperature and EV Discharge","Big Change Temperature and SB Charge20","Big Change Temperature and SB Charge40","Big Change Temperature and SB Charge60","Big Change Temperature and SB Discharge20","Big Change Temperature and SB Discharge40","Big Change Temperature and SB Discharge60","Huge Change Temperature and EV Charge","Huge Change Temperature and EV Discharge","Huge Change Temperature and SB Charge20","Huge Change Temperature and SB Charge40","Huge Change Temperature and SB Charge60","Huge Change Temperature and SB Discharge20","Huge Change Temperature and SB Discharge40","Huge Change Temperature and SB Discharge60","EV Charge and SB Charge20","EV Charge and SB Charge40","EV Charge and SB Charge60","EV Charge and SB Discharge20","EV Charge and SB Discharge40","EV Charge and SB Discharge60","EV Discharge and SB Charge20","EV Discharge and SB Charge40","EV Discharge and SB Charge60","EV Discharge and SB Discharge20","EV Discharge and SB Discharge40","EV Discharge and SB Discharge60","Small Change Temperature, EV Charge and SB Charge20","Small Change Temperature, EV Charge and SB Charge40","Small Change Temperature, EV Charge and SB Charge60","Small Change Temperature, EV Charge and SB Discharge20","Small Change Temperature, EV Charge and SB Discharge40","Small Change Temperature, EV Charge and SB Discharge60","Big Change Temperature, EV Charge and SB Charge20","Big Change Temperature, EV Charge and SB Charge40","Big Change Temperature, EV Charge and SB Charge60","Big Change Temperature, EV Charge and SB Discharge20","Big Change Temperature, EV Charge and SB Discharge40","Big Change Temperature, EV Charge and SB Discharge60","Huge Change Temperature, EV Charge and SB Charge20","Huge Change Temperature, EV Charge and SB Charge40","Huge Change Temperature, EV Charge and SB Charge60","Huge Change Temperature, EV Charge and SB Discharge20","Huge Change Temperature, EV Charge and SB Discharge40","Huge Change Temperature, EV Charge and SB Discharge60"]
            env = classes.UMADemoINC(lstm_pred[0:20])

            done = False
            step = 0
            env.reset()
            results = []
            state = np.array(env.reset())
            policy_network = tf.keras.models.load_model("DataMonitoring/models/{}/{}/{}/policyNetwork.h5".format("REAL","INC", "Dense"))
            while not done:
                state_tensor = tf.convert_to_tensor(state)
                state_tensor = tf.expand_dims(state_tensor, 0)
                action_probs = policy_network(state_tensor, training=False)
                action = tf.argmax(action_probs[0]).numpy()
                state, reward, done, info = env.step(action)
                results.append({'datetime': d.strftime('%d/%m/%Y %H:%M:%S'), "cons_exp" : round(lstm_pred[step],2), "cons": round(-env.get_action_cons(),2), "action": action_values[action] })
                step+=1
                d +=  timedelta(minutes=15)

            return render(request, 'mas.html', {"consumptions" : results, "models_name" : models})
        else:
            return HttpResponseRedirect("Login")

    def post(self, request):
        cookie = request.COOKIES.get('access')
        if cookie != None:
            db = client.Ebalance
            scenario_form = ScenarioForm(request.POST or None)
            if request.method == "POST" and scenario_form.is_valid():
                model_type = scenario_form.cleaned_data["modelType"] if scenario_form.cleaned_data["modelType"] else "Incremental"
                modelSelected = scenario_form.cleaned_data["modelSelected"] if scenario_form.cleaned_data["modelSelected"] else "Dense"
                sc_type = scenario_form.cleaned_data["sc_type"] if scenario_form.cleaned_data["sc_type"] else "REAL"

                model_dense_500 = tf.keras.models.load_model("DataMonitoring/models/model_dense_500.h5")
                model_lstm_250 = tf.keras.models.load_model("DataMonitoring/models/model_lstm_250.h5")
                db = client.Ebalance
                col = db["emv210"]

                data = col.find({},{"datetime" : 1, "kwh_p_tot_r" : 1}).sort("_id", -1) 

                timestamp = pd.to_datetime(data[0]["datetime"])
                dow = timestamp.dayofweek
                timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                day = timestamp[0:2]
                month = timestamp[3:5]
                year = timestamp[6:10]
                hour = timestamp[11:13]
                minute = timestamp[14:16]
                d = datetime(int(year), int(month), int(day), int(hour), int(minute))
                curve = []

                db = client.Ebalance
                col2 = db["openweather"]
                data2 = col2.find().sort("_id", -1)
                scaler = load(open("DataMonitoring/models/cemosa-scaler-forecasting.pkl", 'rb'))
                for x in range(1,97):
                    timestamp = pd.to_datetime(data[96-x]["datetime"])
                    dow = timestamp.dayofweek
                    timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                    day = float(timestamp[0:2])
                    month = float(timestamp[3:5])
                    year = float(timestamp[6:10])
                    hour = float(timestamp[11:13])
                    minute = float(timestamp[14:16])
                    d +=  timedelta(minutes=15)
                    
                    new_x = np.array([[data[96-x]["kwh_p_tot_r"], data2[96-x]["temp_min"] , data2[96-x]["temp_max"], data2[96-x]["humidity"], data2[96-x]["wind"], dow, month, hour, data[192-x]["kwh_p_tot_r"], data[288-x]["kwh_p_tot_r"], data[384-x]["kwh_p_tot_r"], data[480-x]["kwh_p_tot_r"], data[576-x]["kwh_p_tot_r"], data[672-x]["kwh_p_tot_r"], data[768-x]["kwh_p_tot_r"]]])
                    X = scaler.transform(new_x)
                    val1 = model_dense_500.predict(X)
                    val2 = model_lstm_250.predict(X)
                    val = (float(val1[0][0]) + float(val2[0][0]))/2
                    curve.append(val)
                d = datetime(int(year), int(month), int(day), int(hour), int(minute))
    
                policy_network = tf.keras.models.load_model("DataMonitoring/models/{}/{}/{}/policyNetwork.h5".format(sc_type,model_type, modelSelected))
                if sc_type == "REAL":
                    action_values = ["Do nothing.","Small change temperature","Big Change temperature ","Huge Change temperature","EV Charge","EV Discharge","SB Charge20","SB Charge40","SB Charge60","SB Discharge20","SB Discharge40","SB Discharge60","Small Change Temperature and EV Charge","Small Change Temperature and EV Discharge","Small Change Temperature and SB Charge20","Small Change Temperature and SB Charge40","Small Change Temperature and SB Charge20","Small Change Temperature and SB Discharge20","Small Change Temperature and SB Discharge40","Small Change Temperature and SB Discharge60","Big Change Temperature and EV Charge","Big Change Temperature and EV Discharge","Big Change Temperature and SB Charge20","Big Change Temperature and SB Charge40","Big Change Temperature and SB Charge60","Big Change Temperature and SB Discharge20","Big Change Temperature and SB Discharge40","Big Change Temperature and SB Discharge60","Huge Change Temperature and EV Charge","Huge Change Temperature and EV Discharge","Huge Change Temperature and SB Charge20","Huge Change Temperature and SB Charge40","Huge Change Temperature and SB Charge60","Huge Change Temperature and SB Discharge20","Huge Change Temperature and SB Discharge40","Huge Change Temperature and SB Discharge60","EV Charge and SB Charge20","EV Charge and SB Charge40","EV Charge and SB Charge60","EV Charge and SB Discharge20","EV Charge and SB Discharge40","EV Charge and SB Discharge60","EV Discharge and SB Charge20","EV Discharge and SB Charge40","EV Discharge and SB Charge60","EV Discharge and SB Discharge20","EV Discharge and SB Discharge40","EV Discharge and SB Discharge60","Small Change Temperature, EV Charge and SB Charge20","Small Change Temperature, EV Charge and SB Charge40","Small Change Temperature, EV Charge and SB Charge60","Small Change Temperature, EV Charge and SB Discharge20","Small Change Temperature, EV Charge and SB Discharge40","Small Change Temperature, EV Charge and SB Discharge60","Big Change Temperature, EV Charge and SB Charge20","Big Change Temperature, EV Charge and SB Charge40","Big Change Temperature, EV Charge and SB Charge60","Big Change Temperature, EV Charge and SB Discharge20","Big Change Temperature, EV Charge and SB Discharge40","Big Change Temperature, EV Charge and SB Discharge60","Huge Change Temperature, EV Charge and SB Charge20","Huge Change Temperature, EV Charge and SB Charge40","Huge Change Temperature, EV Charge and SB Charge60","Huge Change Temperature, EV Charge and SB Discharge20","Huge Change Temperature, EV Charge and SB Discharge40","Huge Change Temperature, EV Charge and SB Discharge60"]
                    if model_type == "INC":
                        env = classes.UMADemoINC(curve[0:20])
                    elif model_type == "DEC":
                        env = classes.UMADemoDEC(curve[0:20])
                elif sc_type == "No_Car":
                    action_values = ["Do nothing.","Small change temperature","Big Change temperature","Huge Change temperature","SB Charge20","B Charge40","SB Charge60","SB Discharge20","SB Discharge40","SB Discharge60","Small Change Temperature and SB Charge20","Small Change Temperature and SB Charge40","Small Change Temperature and SB Charge20","Small Change Temperature and SB Discharge20","Small Change Temperature and SB Discharge40","Small Change Temperature and SB Discharge60","Big Change Temperature and SB Charge20","Big Change Temperature and SB Charge40","Big Change Temperature and SB Charge60","Big Change Temperature and SB Discharge20","Big Change Temperature and SB Discharge40","Big Change Temperature and SB Discharge60","Huge Change Temperature and SB Charge20","Huge Change Temperature and SB Charge40","Huge Change Temperature and SB Charge60","Huge Change Temperature and SB Discharge20","Huge Change Temperature and SB Discharge40","Huge Change Temperature and SB Discharge60"]
                    if model_type == "INC":
                        env = classes.UMADemoINC_No_Car(curve[0:20])
                    elif model_type == "DEC":
                        env = classes.UMADemoDEC_No_Car(curve[0:20])
                elif sc_type == "No_Bat":
                    action_values = ["Do nothing.","Small change temperature","Big Change temperature", "SB Charge20", "SB Charge40", "SB Charge60", "SB Discharge20", "SB Discharge40", "SB Discharge60", "Small Change Temperature and SB Charge20", "Small Change Temperature and SB Charge40", "Small Change Temperature and SB Charge20" , "Small Change Temperature and SB Discharge20" , "Small Change Temperature and SB Discharge40", "Small Change Temperature and SB Discharge60", "Big Change Temperature and SB Charge20", "Big Change Temperature and SB Charge40", "Big Change Temperature and SB Charge60", "Big Change Temperature and SB Discharge20", "Big Change Temperature and SB Discharge40", "Big Change Temperature and SB Discharge60"]
                    if model_type == "INC":
                        env = classes.UMADemoINC_No_Batteries(curve[0:20])
                    elif model_type == "DEC":
                        env = classes.UMADemoDEC_No_Batteries(curve[0:20])
                done = False
                step = 0
                env.reset()
                results = []
                state = np.array(env.reset())
                while not done:
                    state_tensor = tf.convert_to_tensor(state)
                    state_tensor = tf.expand_dims(state_tensor, 0)
                    action_probs = policy_network(state_tensor, training=False)
                    action = tf.argmax(action_probs[0]).numpy()
                    state, reward, done, info = env.step(action)
                    step+=1
                    results.append({'datetime': d.strftime('%d/%m/%Y %H:%M:%S'), "cons_exp" : round(curve[step],2), "cons": round(-env.get_action_cons(),2), "action": action_values[action] })
                    d +=  timedelta(minutes=15)
                return render(request, 'mas.html', {"consumptions" : results})


        else:
            return HttpResponseRedirect("Login")



class ConsumptionsView(TemplateView):
    def get(self, request):
        cookie = request.COOKIES.get('access')
        if cookie != None:
            db = client.Ebalance
            col = db["emv210"]
            data = col.find({},{"datetime" : 1, "v_l1_n" :1, "v_l2_n" : 1, "v_l3_n": 1, "v_l1_l2": 1, "v_l2_l3" : 1, "v_l3_l1": 1, "a_l1": 1, "a_l2": 1, "a_l3": 1, "w_l1": 1, "w_l2": 1, "w_l3":1  ,"kwh_p_tot_r" : 1}).sort("_id", -1).limit(25) 
            return render(request, 'consumptions.html', {"data" : data, "num_registers": 25})
        else:
            return HttpResponseRedirect("Login")
    def post(self, request):
        consumptions_form = ConsumptionsForm(request.POST or None)
        if request.method == "POST" and consumptions_form.is_valid():
            registers = consumptions_form.cleaned_data["num_registers"] if consumptions_form.cleaned_data["num_registers"] else None
            if registers != None:
                db = client.Ebalance
                col = db["emv210"]
                data = col.find({},{"datetime" : 1, "v_l1_n" :1, "v_l2_n" : 1, "v_l3_n": 1, "v_l1_l2": 1, "v_l2_l3" : 1, "v_l3_l1": 1, "a_l1": 1, "a_l2": 1, "a_l3": 1, "w_l1": 1, "w_l2": 1, "w_l3":1  ,"kwh_p_tot_r" : 1}).sort("_id", -1).limit(int(registers)) 
                return render(request, 'consumptions.html', {"data" : data, "num_registers": registers})
        return HttpResponseRedirect("Login")




class ModelsProcessingView(TemplateView):
    def get(self, request):
            return JsonResponse({"STATUS" : 200})
    def post(self, request):
        for filename, f in request.FILES.items():
            name = request.FILES[filename].name
            if name == "directory":
                print("ENTRA DIRECTORY: " ,name)
                directory = f.read().decode("utf-8")
                os.makedirs("DataMonitoring/models/"+directory)
                os.makedirs("DataMonitoring/models/"+directory+"/variables")
                os.makedirs("DataMonitoring/models/"+directory+"/assets")
            elif name == "variables.data-00000-of-00001" or name == "variables.index":
                print("ENTRA VARIABLES: " ,name)
                new_file = open("DataMonitoring/models/"+directory+"/variables/"+name, "wb+")
                new_file.write(f.read())
                new_file.close()
            elif name == "policy_specs.pbtxt":
                print("ENTRA policy_specs: " ,name)
                new_file = open("DataMonitoring/models/"+directory+"/"+name, "wb+")
                new_file.write(f.read())
                new_file.close()
            elif name == "saved_model.pb":
                print("ENTRA SAVED_MODELS: ", name)
                new_file = open("DataMonitoring/models/"+directory+"/"+name, "wb+")
                new_file.write(f.read())
                new_file.close()


        return JsonResponse({"STATUS" : 200})



class ForeCastingAPIRestView(TemplateView):
    def get(self, request):
        model_dense_500 = tf.keras.models.load_model("DataMonitoring/models/model_dense_500.h5")
        model_lstm_250 = tf.keras.models.load_model("DataMonitoring/models/model_lstm_250.h5")
        db = client.Ebalance
        col = db["emv210"]

        data = col.find({},{"datetime" : 1, "kwh_p_tot_r" : 1}).sort("_id", -1) 

        timestamp = pd.to_datetime(data[0]["datetime"])
        dow = timestamp.dayofweek
        timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
        day = timestamp[0:2]
        month = timestamp[3:5]
        year = timestamp[6:10]
        hour = timestamp[11:13]
        minute = timestamp[14:16]
        d = datetime(int(year), int(month), int(day), int(hour), int(minute))
        curve = []

        db = client.Ebalance
        col2 = db["openweather"]
        data2 = col2.find().sort("_id", -1)
        scaler = load(open("DataMonitoring/models/cemosa-scaler-forecasting.pkl", 'rb'))
        for x in range(1,97):
            timestamp = pd.to_datetime(data[96-x]["datetime"])
            dow = timestamp.dayofweek
            timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            day = float(timestamp[0:2])
            month = float(timestamp[3:5])
            year = float(timestamp[6:10])
            hour = float(timestamp[11:13])
            minute = float(timestamp[14:16])
            d +=  timedelta(minutes=15)
            
            new_x = np.array([[data[96-x]["kwh_p_tot_r"], data2[96-x]["temp_min"] , data2[96-x]["temp_max"], data2[96-x]["humidity"], data2[96-x]["wind"], dow, month, hour, data[192-x]["kwh_p_tot_r"], data[288-x]["kwh_p_tot_r"], data[384-x]["kwh_p_tot_r"], data[480-x]["kwh_p_tot_r"], data[576-x]["kwh_p_tot_r"], data[672-x]["kwh_p_tot_r"], data[768-x]["kwh_p_tot_r"]]])
            X = scaler.transform(new_x)
            val1 = model_dense_500.predict(X)
            val2 = model_lstm_250.predict(X)
            val = (float(val1[0][0]) + float(val2[0][0]))/2
            curve.append({'datetime': d.strftime('%d/%m/%Y %H:%M:%S') , 'value':round(val,2)})
        return JsonResponse({"STATUS" : 200, "data" : curve})
    def post(self, request):
        return JsonResponse({"STATUS" : 200})



class ActionListAPIRestView(TemplateView):
    def get(self, request):

        flexibility = float(request.GET.get('flexibility', 20.0))

        model_dense_500 = tf.keras.models.load_model("DataMonitoring/models/model_dense_500.h5")
        model_lstm_250 = tf.keras.models.load_model("DataMonitoring/models/model_lstm_250.h5")
        db = client.Ebalance
        col = db["emv210"]

        data = col.find({},{"datetime" : 1, "kwh_p_tot_r" : 1}).sort("_id", -1) 

        timestamp = pd.to_datetime(data[0]["datetime"])
        dow = timestamp.dayofweek
        timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
        day = timestamp[0:2]
        month = timestamp[3:5]
        year = timestamp[6:10]
        hour = timestamp[11:13]
        minute = timestamp[14:16]
        d = datetime(int(year), int(month), int(day), int(hour), int(minute))
        curve = []

        db = client.Ebalance
        col2 = db["openweather"]
        data2 = col2.find().sort("_id", -1)
        scaler = load(open("DataMonitoring/models/cemosa-scaler-forecasting.pkl", 'rb'))
        for x in range(1,97):
            timestamp = pd.to_datetime(data[96-x]["datetime"])
            dow = timestamp.dayofweek
            timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            day = float(timestamp[0:2])
            month = float(timestamp[3:5])
            year = float(timestamp[6:10])
            hour = float(timestamp[11:13])
            minute = float(timestamp[14:16])
            d +=  timedelta(minutes=15)
            
            new_x = np.array([[data[96-x]["kwh_p_tot_r"], data2[96-x]["temp_min"] , data2[96-x]["temp_max"], data2[96-x]["humidity"], data2[96-x]["wind"], dow, month, hour, data[192-x]["kwh_p_tot_r"], data[288-x]["kwh_p_tot_r"], data[384-x]["kwh_p_tot_r"], data[480-x]["kwh_p_tot_r"], data[576-x]["kwh_p_tot_r"], data[672-x]["kwh_p_tot_r"], data[768-x]["kwh_p_tot_r"]]])
            X = scaler.transform(new_x)
            val1 = model_dense_500.predict(X)
            val2 = model_lstm_250.predict(X)
            val = (float(val1[0][0]) + float(val2[0][0]))/2
            curve.append(val)

        action_values = ["Do nothing", "Small change temperature", "Big Change temperature", "EV Charge", "EV Discharge", "SB Charge20", "SB Charge40" ,"SB Charge60", "SB Discharge20" ,"SB Discharge40", "SB Discharge60", "Small Change Temperature and EV Charge", "Small Change Temperature and EV Discharge", "Small Change Temperature and SB Charge20", "Small Change Temperature and SB Charge40", "Small Change Temperature and SB Charge60", "Small Change Temperature and SB Discharge20", "Small Change Temperature and SB Discharge40", "Small Change Temperature and SB Discharge60", "Big Change Temperature and EV Charge", "Big Change Temperature and EV Discharge", "Big Change Temperature and SB Charge20", "Big Change Temperature and SB Charge40", "#Big Change Temperature and SB Charge60", "Big Change Temperature and SB Discharge20", "Big Change Temperature and SB Discharge40", "Big Change Temperature and SB Discharge60", "EV Charge and SB Charge20", "EV Charge and SB Charge40", "EV Charge and SB Charge60", "EV Charge and SB Discharge20", "EV Charge and SB Discharge40", "EV Charge and SB Discharge60", "EV Discharge and SB Charge20", "EV Discharge and SB Charge40", "EV Discharge and SB Charge60", "EV Discharge and SB Discharge20", "EV Discharge and SB Discharge40", "EV Discharge and SB Discharge60", "Small Change Temperature, EV Charge and SB Charge20", "Small Change Temperature, EV Charge and SB Charge40", "Small Change Temperature, EV Charge and SB Charge60", "EV Charge and SB Discharge20", "Small Change Temperature, EV Charge and SB Discharge40", "Small Change Temperature, EV Charge and SB Discharge60", "Big Change Temperature, EV Charge and SB Charge20", "Big Change Temperature, EV Charge and SB Charge40", "Big Change Temperature, EV Charge and SB Charge60", "Big Change Temperature, EV Charge and SB Discharge20", "Big Change Temperature, EV Charge and SB Discharge40",  "Big Change Temperature, EV Charge and SB Discharge60"]
        env = classes.RealScenario(curve, flexibility=200000.0)
        eval_py_env = wrappers.TimeLimit(classes.RealScenario(curve, flexibility=200000.0), duration=1000)
        eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)
        saved_policy = tf.saved_model.load('DataMonitoring/models/policy')
        action_list = []
        env.reset()
        cont = 0
        time_step = eval_env._reset()
        results = []
        d = datetime(int(year), int(month), int(day), int(hour), int(minute))

        while not time_step.is_last():
            d += timedelta(minutes=15)
            action_step = saved_policy.action(time_step)
            action_list.append(tf.get_static_value(action_step.action[0]))
            time_step = eval_env.step(action_step.action)
            env.step(action_step.action)
            
            results.append({'datetime': d.strftime('%d/%m/%Y %H:%M:%S'), "cons_exp" : round(curve[cont],2), "cons": env.get_consumption(), "cumulative_cons" : round(env.get_cumulative_consumption(),2), "action": action_values[action_step.action[0]] })
            cont+=1


        return JsonResponse({"STATUS" : 200, "data" : results})
    def post(self, request):
        return JsonResponse({"STATUS" : 200})


class ConsumptionsAPIRestView(TemplateView):
    def get(self, request):
        num = int(request.GET.get('registers', 1000000))
        db = client.Ebalance
        col = db["emv210"]
        data = col.find({},{"_id" : -1}).sort("_id", -1).limit(num)
        list_cur = list(data)
        json_data = dumps(list_cur)
        return JsonResponse({"STATUS" : 200, "data" : json_data})
    def post(self, request):
        return JsonResponse({"STATUS" : 200})

class WeatherAPIRestView(TemplateView):
    def get(self, request):
        num = int(request.GET.get('registers', 1000000))
        db = client.Ebalance
        col = db["openweather"]
        data = col.find({},{"_id" : -1}).sort("_id", -1).limit(num)
        list_cur = list(data)
        json_data = dumps(list_cur)

        return JsonResponse({"STATUS" : 200, "data" : json_data})
    def post(self, request):
        return JsonResponse({"STATUS" : 200})




class FlexForm(forms.Form):
   flex = forms.FloatField(required=False)


class LoginForm(forms.Form):
    user = forms.CharField()
    passw = forms.CharField()

class ScenarioForm(forms.Form):
    modelSelected = forms.CharField()
    modelType = forms.CharField()
    sc_type = forms.CharField()

class ConsumptionsForm(forms.Form):
    num_registers = forms.IntegerField()

class ModelForm(forms.Form):
    CHOICES=[('0', 0),('1',1), ('2', 2)]
    model_name = forms.CharField()
    scenario_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    flex = forms.FloatField()
    soc = forms.FloatField()
    num_iterations = forms.IntegerField()




