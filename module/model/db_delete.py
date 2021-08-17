import pymongo
import pandas as pd
from datetime import timedelta, date, datetime
import random
import string
from ..model import db_query,db_insert
from bson.objectid import ObjectId

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

def delete_record(date,delete_index):
    date = date.split('-')
    year = date[0]
    month = date[1]    
    collection = db["workingHoursRecord"]
    try:
        query = {
            'month':month
        }
        result = list(collection.find(query).sort([('date', 1)]).limit(delete_index))
        query = {
            '_id':ObjectId(result[-1]['_id'])
        }
        record_date = result[-1]['date']
        collection.delete_one(query)
        db_insert.update_daily_working_hours(record_date)
        return True
    except Exception as e:
        print("Error message: ", e)    
        return False  
