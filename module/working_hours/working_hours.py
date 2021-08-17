from . import working_hours_api
from module.model import db_insert,db_query,db_delete
from flask import render_template, request, jsonify, send_file, safe_join
import json, threading
import os
from datetime import timedelta, date, datetime
import time
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import decode_token
this_month_working_hours_target = 20.5
_Response = {
    "responseText": None,
    "sucess": True,
    "status_code": 200,            
    }   

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


@working_hours_api.route('/historyData', methods=['GET', 'POST'])
def history_data():

    print("The history_data API is called")
    year = datetime.today().strftime("%Y")
    month = datetime.today().strftime("%m")
    num_day_of_month = get_num_day_of_month(year,month)
    start_time = year + '/' + month + '/' + '01'
    finish_time = year + '/' + month + '/' + str(num_day_of_month+1)
    
    table_data = db_query.query_working_hours_record_detail(start_time,finish_time)
    
    if table_data == []:
        return render_template("historyData.html",table_data = [] )   
    else:
        result_table_data = []
        this_month_total_hours = 0
        this_month_total_minute = 0 
        for data in table_data:
            result_hour,result_minute = tran_minute_to_hour(data['totalWorkingHours'])
            result_table_data.append([data['date'],data['startAt'],data['finishAt'],data['type'],int(result_hour),int(result_minute)])
            this_month_total_minute += data['totalWorkingHours']
            
        this_month_total_hours,this_month_total_minute = tran_minute_to_hour(this_month_total_minute)
        
        return render_template("historyData.html",table_data = result_table_data,header_month_hour = this_month_total_hours,header_month_minute = this_month_total_minute)
    return render_template("historyData.html") 

@working_hours_api.route('/historyDataByMonth', methods=['GET', 'POST'])
def history_data_by_month():
    if request.method=='POST':
        data = request.get_json()['month']
        
        print("The history_data API is called")
        
        data = data.split('-')
        year = data[0]
        month = data[1]
        num_day_of_month = get_num_day_of_month(year,month)
        start_time = year + '/' + month + '/' + '01'
        finish_time = year + '/' + month + '/' + str(num_day_of_month+1)
        table_data = db_query.query_working_hours_record_detail(start_time,finish_time)

        if table_data == []:
            _Response["responseText"] = render_template("historyDataTable.html",table_data = [] )   
            return jsonify(_Response)
        else:
            this_month_total_hours = 0
            this_month_total_minute = 0             
            result_table_data = []
            for data in table_data:
                result_hour,result_minute = tran_minute_to_hour(data['totalWorkingHours'])
                result_table_data.append([data['date'],data['startAt'],data['finishAt'],data['type'],int(result_hour),int(result_minute)])
                this_month_total_minute += data['totalWorkingHours']
            
            this_month_total_hours,this_month_total_minute = tran_minute_to_hour(this_month_total_minute)
            _Response["responseText"] = render_template("historyDataTable.html",table_data = result_table_data,header_month_hour = this_month_total_hours,header_month_minute = this_month_total_minute)   
            return jsonify(_Response)

        return render_template("historyData.html")  


@working_hours_api.route('/deleteRecord', methods=['GET', 'POST'])
def delete_record():
    if request.method=='POST':
        date = request.get_json()['month']
        delete_index = request.get_json()['deleteIndex']
        print("The delete_record API is called")
        

        
        
        
        db_delete.delete_record(date,delete_index)
        date = date.split('-')
        year = date[0]
        month = date[1]
        print(month,delete_index)
        num_day_of_month = get_num_day_of_month(year,month)
        start_time = year + '/' + month + '/' + '01'
        finish_time = year + '/' + month + '/' + str(num_day_of_month+1)        
        
        table_data = db_query.query_working_hours_record_detail(start_time,finish_time)

        if table_data == []:
            _Response["responseText"] = render_template("historyDataTable.html",table_data = [] )   
            return jsonify(_Response)
        else:
            result_table_data = []
            for data in table_data:
                result_hour,result_minute = tran_minute_to_hour(data['totalWorkingHours'])
                result_table_data.append([data['date'],data['startAt'],data['finishAt'],data['type'],int(result_hour),int(result_minute)])
            _Response["responseText"] = render_template("historyDataTable.html",table_data = result_table_data)   
            return jsonify(_Response)
        
        return render_template("historyData.html")  
    
    

@working_hours_api.route('/workingHours', methods=['GET', 'POST'])
def working_hours():

    print("The working_hours API is called")
    
    today = datetime.today().strftime("%Y/%m/%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y/%m/%d")
    now_time = datetime.today().strftime("%H:%M")

    table_data = db_query.query_working_hours_record_detail(today,tomorrow) 
    this_month_record = db_query.query_daily_working_hours_record_by_month(today[5:7])
    this_month_total_hours = 0
    this_month_total_minute = 0 
    this_month_left_hours = 0
    this_month_left_minute = 0 
    if this_month_record != []:
        for record in this_month_record:
            tmp = record['totalWorkingHours'].split(':')
            this_month_total_hours += int(tmp[0])
            this_month_total_minute += int(tmp[1])
        this_month_left_hours,this_month_left_minute = tran_minute_to_hour(8*this_month_working_hours_target*60 - this_month_total_hours * 60 - this_month_total_minute)
        this_month_total_hours,this_month_total_minute = tran_minute_to_hour(this_month_total_hours * 60 + this_month_total_minute)
            
    result_total_hour = 0
    result_total_minute = 0
    result_left_hour = 0
    result_left_minute = 0
    result_table_data = []

    for data in table_data:
        hour,minute = tran_minute_to_hour(data['totalWorkingHours'])
        result_table_data.append([data['startAt'],data['finishAt'],data['type'],int(hour),int(minute)])
        result_total_hour += int(hour)
        result_total_minute += int(minute)

    #計算最後一次工作起始時間工作了多久
    if result_table_data!=[] and result_table_data[-1][1] == '':
        now_time = now_time.split(':')
        tmp_time = result_table_data[-1][0].split(':')
        tmp_interval = int(now_time[0])*60 + int(now_time[1]) - int(tmp_time[0])*60 - int(tmp_time[1])
        tmp_hour,tmp_minute = tran_minute_to_hour(tmp_interval)
        result_table_data[-1][3] = tmp_hour
        result_table_data[-1][4] =tmp_minute
        result_total_minute += tmp_minute  
        result_total_hour = result_total_hour + tmp_hour


    result_total_hour = result_total_hour + result_total_minute//60 
    result_total_minute = result_total_minute -  result_total_minute//60 * 60 

    tmp_minute =  8 * 60 - result_total_hour * 60 -  result_total_minute  
    if tmp_minute < 0:
        result_left_hour,result_left_minute =0,0   
    else:
        result_left_hour,result_left_minute = tran_minute_to_hour(tmp_minute)

    return render_template("workingHours.html",header_month_hour = this_month_total_hours,header_month_minute = this_month_total_minute,table_data = result_table_data,header_today_hour = result_total_hour,header_today_minute = result_total_minute,today_left_hour = result_left_hour,today_left_minute = result_left_minute,month_left_hour = this_month_left_hours,month_left_minute = this_month_left_minute)    
       


@working_hours_api.route('/chart', methods=['GET', 'POST'])
def chart():

    print("The chart_data API is called")
    

    return render_template("chart.html")  


@working_hours_api.route('/sendStartAt', methods=['GET', 'POST'])
def send_start_at():
    now_time = datetime.today().strftime("%H:%M")
    today = datetime.today().strftime("%Y/%m/%d")
    print("The get_start_at API is called")
    
    if request.method=='POST':
        start_at = request.get_json()['startAt']
        if start_at == "":
            start_at = now_time  
            
        flag = db_insert.insert_start_at(start_at,today)
        if flag:
            _Response["responseText"] = "success"
        else:
            _Response["responseText"] = "failure"
        return jsonify(_Response)
    
@working_hours_api.route('/sendFinishAt', methods=['GET', 'POST'])
def send_finish_at():
                                         
    now_time = datetime.today().strftime("%H:%M")
    today = datetime.today().strftime("%Y/%m/%d")
    print("The send_finish_at API is called")
    
    if request.method=='POST':
        start_at = request.get_json()['startAt']
        finish_at = request.get_json()['finishAt']
        _type = request.get_json()['type']
        
        
        if _type == "":
            _type = "一般"
        if finish_at == "":
            finish_at = now_time
        if start_at !='':
            flag = db_insert.insert_start_at(start_at,today)
            if flag == False:
                _Response["responseText"] = "failure"
                return jsonify(_Response)       

        flag = db_insert.insert_finish_at(finish_at,_type,today)
        
        if flag == "No start at":
            _Response["responseText"] = "No start at"
            return jsonify(_Response)    
        
        elif flag == True:
            flag2 = db_insert.update_daily_working_hours(today)
            if flag2 == False:
                _Response["responseText"] = "failure"
                return jsonify(_Response)    
            
            _Response["responseText"] = "success"

        else:
            _Response["responseText"] = "failure"
        return jsonify(_Response)    
#補打卡
@working_hours_api.route('/checkIn', methods=['GET', 'POST'])
def check_in():
                                         
    now_time = datetime.today().strftime("%H:%M")
    today = datetime.today().strftime("%Y/%m/%d")
    print("The checkIn API is called")
    
    if request.method=='POST':
        start_at = request.get_json()['startAt']
        finish_at = request.get_json()['finishAt']
        _type = request.get_json()['type']
 
        record_date = request.get_json()['workingHoursDate']
        record_date = record_date.replace('-','/')

            
            
        
        if _type == "":
            _type = "一般"
        if finish_at == "":
            finish_at = now_time
        if start_at !='':
            flag = db_insert.insert_start_at(start_at,record_date)
            if flag == False:
                _Response["responseText"] = "failure"
                return jsonify(_Response)       

        flag = db_insert.insert_finish_at(finish_at,_type,record_date)
        
        if flag == "No start at":
            _Response["responseText"] = "No start at"
            return jsonify(_Response)    
        
        elif flag == True:
            flag2 = db_insert.update_daily_working_hours(record_date)
            if flag2 == False:
                _Response["responseText"] = "failure"
                return jsonify(_Response)    
            
            _Response["responseText"] = "success"

        else:
            _Response["responseText"] = "failure"
        return jsonify(_Response)    
    
        