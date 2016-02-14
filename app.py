import rauth
import numpy as np
import pandas as pd
import time
import json
import urllib2
import math 
from flask import Flask, render_template, request, redirect, url_for
import os

#from config import *

app = Flask(__name__)

def get_results(params):
 
  #Obtain these from Yelp's manage access page
  session = rauth.OAuth1Session(
    consumer_key = os.environ['yelp_consumer_key']
    ,consumer_secret = os.environ['yelp_consumer_secret']
    ,access_token = os.environ['yelp_token']
    ,access_token_secret = os.environ['yelp_token_secret'])
     
  request = session.get("http://api.yelp.com/v2/search",params=params)
   
  #Transforms the JSON API response into a Python dictionary
  return request.json()

def latlong(address):
  address = urllib2.quote(address)
  key = urllib2.quote(google_geocode_api_key)
  geocodeURL = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (address, key)
  request = urllib2.urlopen(geocodeURL)
  jsonResponse = json.loads(request.read())
  data = jsonResponse[jsonResponse.keys()[1]]
  df = pd.DataFrame.from_dict(data)
  lat = df.geometry[0]['location']['lat']
  lng = df.geometry[0]['location']['lng']
  return lat, lng

def get_search_parameters(lat,lng,cuisine):
  #See the Yelp API for more details woo
  params = {}
  params["term"] = cuisine
  params["ll"] = "{},{}".format(str(lat),str(lng))
  params["radius_filter"] = "20000"
  params["limit"] = "20"
  params["category_filter"] = "restaurants"
  params["sort"] = "2"
  return params

def haversineDistMiles(lat1, lng1, lat2, lng2):
  # convert decimal to radians
  lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
  h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)* math.sin((lng2-lng1)/2)**2
  return 2*math.asin(math.sqrt(h))*3959 
  
def make_plot(df, which_cuisine):
    p4 = Bar(df, values = 'rating',\
             label = 'name', agg = 'max', color = "wheat", \
             title = 'Best '+which_cuisine+' by star rating alone', \
             xlabel = 'Restaurant name', ylabel = 'Star rating')
    output_file("templates/plots.html")
    #p = vplot(p4)
    show(p4)

@app.route("/")
def main():
  return redirect("/index")

@app.route("/index", methods = ['GET', 'POST'])
def bestFive():
  if request.method == 'GET':
    return render_template('index.html')
  else:
    address = request.form['address']
    cuisine = request.form['cuisine']
    lat,lng = latlong(address)
    params = get_search_parameters(lat,lng, cuisine)
    data = get_results(params)
    #Be a good internet citizen and rate-limit yourself
    time.sleep(1.0)
    data = data[data.keys()[2]]
    df = pd.DataFrame.from_dict(data)
    markerList = []
    restaurantInfo = []
    for i in range(0,5):
      markerList.append([str(df.name[i]), \
                         df.location[i]['coordinate']['latitude'], \
                         df.location[i]['coordinate']['longitude']])
      restaurantInfo.append([str(df.name[i]),\
                             str(df.url[i]),\
                             str(df.display_phone[i])])
    KEY = os.environ['googleJsapi']
    return render_template("map3.html", \
                           markerList = markerList, \
                           restaurantInfo = restaurantInfo,  KEY = KEY)
                    

if __name__=="__main__":
  app.run(debug = True)



