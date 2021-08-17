import pymongo
import pandas as pd
from datetime import timedelta, date, datetime
import random
import string
from ..model import db_query

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["workingHoursSystem"]
def get_num_day_of_month(year,month):
    if month in ['01','03','05','07','08','10','12']:
        return 31
    elif month in ['04','06','09','11']:
        return 30
    else:
        if int(year) % 4 == 0:
            return 29
        else:
            return 28

def tran_minute_to_hour(minute):
    hour = minute // 60
    minute = minute - hour * 60 
    return hour,minute
def get_interval_between_time(start_at,finish_at,_type):
    start_at = start_at.split(":")
    finish_at = finish_at.split(":")
    
    start_at = int(start_at[0])*60 + int(start_at[1])
    finish_at = int(finish_at[0])*60 + int(finish_at[1])
    
    result = finish_at - start_at
    if _type == "NBA":
        result = result/2
    return result

def insert_start_at(start_at,record_date):
    collection = db["workingHoursRecord"]
    today = datetime.today().strftime("%Y/%m/%d")
    now_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    data = {
        "year":record_date[:4],
        "month":record_date[5:7],
        "day":record_date[8:10],
        "date":record_date,
        "type":"",
        "insertAt":now_time,  
        "startAt":start_at,      
        "finishAt":"",      
        "insertAt2":"",      
        "totalWorkingHours":0,      
    }
    try:
        collection.insert_one(data)  
        return True
    except Exception as e:
        print("Error message: ", e)    
        return False  
def update_daily_working_hours(record_date):
    today = record_date
    tomorrow = record_date + ' 11:59:59'
    now_time = datetime.today().strftime("%H:%M")
    print(today,tomorrow)
    today_working_hours_record = db_query.query_working_hours_record_detail(record_date,tomorrow)   
    
    today_total_minute = 0
    for record in today_working_hours_record:
        tmp = record['totalWorkingHours']  
        today_total_minute += tmp
    #print("today_total_minute",today_total_minute)    
    today_total_hour, today_total_minute = tran_minute_to_hour(today_total_minute)    
   
    collection = db["dailyWorkingHoursRecord"]
    query = {'date':today}  

    update_data = {"$set":{"totalWorkingHours":str(int(today_total_hour))+':'+str(int(today_total_minute))}}
    try:
        result = list(collection.find(query))
        if result == []:
            data = {
                "year":today[:4],
                "month":today[5:7],
                "day":today[8:10],
                "date":today,
                "totalWorkingHours":str(int(today_total_hour))+':'+str(int(today_total_minute)),      
            }
            collection.insert_one(data)
        else:
            print("sdfsdfsdf",query) 
            collection.update_one(query,update_data)
        return True
    except Exception as e:
        print("Error message: ", e)    
        return False  
    
def insert_finish_at(finish_at,_type,record_date):
    collection = db["workingHoursRecord"]
    today = datetime.today().strftime("%Y/%m/%d")
    now_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    query = {
        "year":record_date[:4],
        "month":record_date[5:7],
        "day":record_date[8:10],
        "finishAt":'',
    }   
    field_show = {
        "_id":1,"startAt":1,
    }
    result = list(collection.find(query,field_show).sort([('insertAt', -1)]).limit(-1))
    if result == []:
        return "No start at"
    
    
    total_working_hours = get_interval_between_time(result[0]["startAt"],finish_at,_type)
    
    query = {
        "_id":result[0]["_id"],
    }       
    
    data = {
        "$set":
        {
            "year":record_date[:4],
            "month":record_date[5:7],
            "day":record_date[8:10],
            "date":record_date,
            "type":_type,
            "finishAt":finish_at,      
            "insertAt2":now_time,      
            "totalWorkingHours":total_working_hours,      
        }
    }
    try:
        collection.update_one(query,data)
        return True
    except Exception as e:
        print("Error message: ", e)    
        return False  
