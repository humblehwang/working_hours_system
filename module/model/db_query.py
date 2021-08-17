import pymongo
import pandas as pd
from datetime import timedelta, date, datetime
import random
import string

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["workingHoursSystem"]

def query_working_hours_record_detail(start_date,finish_date):
    col = db["workingHoursRecord"]
    query = {
        "$and":
        [
        {"date":{"$gte":start_date}}
        ,{"date":{"$lte":finish_date}}

        ]
    }
    field_show = { "_id":0,"date":1,"startAt":1,"finishAt":1,"type":1,"totalWorkingHours":1}
    try:
        result = list(col.find(query,field_show).sort([('date', 1)]))
        return result
    except Exception as e:
        print("query_working_hours_record_detail failure")
        print("Error message: ", e)    
        return False
    
def query_daily_working_hours_record_by_month(target_month):
    col = db["dailyWorkingHoursRecord"]
    query = {
        "month":target_month
    }
    field_show = { "_id":0,"date":1,"totalWorkingHours":1}
    try:
        result = list(col.find(query,field_show))
        return result
    except Exception as e:
        print("query_daily_working_hours_record_by_month failure")
        print("Error message: ", e)    
        return False  
