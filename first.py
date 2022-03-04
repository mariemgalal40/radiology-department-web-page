from __future__ import print_function
from flask import Flask, render_template, request,url_for,session,send_file
from io import BytesIO
from wtforms import SubmitField
from flask_wtf import Form
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import mysql.connector
import re 
import datetime
import pickle
import os.path

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="mysql",
    database="pythonlogin1"
)
mycursor = mydb.cursor()

  
app = Flask(__name__)
@app.route('/')
def first():
    return render_template('try.html')

@app.route("/patient/results", methods=["GET", "POST"])
def results():
    if request.method == "POST":
        radtype = request.form["rad_type"]
        SSN = request.form["SSN"]
        sql = "SELECT * FROM data WHERE radtype= %s and SSN= %s "
        val = (radtype, SSN)
        mycursor.execute(sql, val)
        for x in mycursor.fetchall():
            name_v=x[3]
            data_v=x[0]
            mydb.commit()
            return send_file (BytesIO(data_v),attachment_filename=str(name_v ),as_attachment=True  )
    return render_template("results.html" )

@app.route('/patient', methods=['POST', 'GET'])
def patientsignin1():
    if request.method == 'POST':
        name = request.form['name']
        ssn = request.form['ssn']
        sql = 'SELECT * FROM patient WHERE name = %s AND ssn = %s'
        val = (name, ssn)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        if result is None:
            return render_template('patient.html',error="Something Went wrong ")
        else:
          return render_template('patienthome.html')
    else:
        return render_template('patient.html')


@app.route('/patient/patientsignup', methods=['POST', 'GET'])
def patient_signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone_number = request.form['phone_number']
        ssn = request.form['ssn']
        try:
            sql = "INSERT INTO patient (name,age,phone_number,ssn) VALUES (%s,%s,%s,%s)"
            val = (name, age, phone_number, ssn, )
            mycursor.execute(sql, val)
            mydb.commit()
            return render_template('patientsignup.html', pmsg="signed up successfully")
        except :
            return render_template('patientsignup.html', ppmsg="invalid ssn")

    else:
        return render_template('patientsignup.html')


@app.route('/doctor', methods=['POST', 'GET'])
def doctor():
    if request.method == 'POST':
        Name = request.form['Name']
        Id = request.form['Id']
        sql = 'SELECT * FROM doctors WHERE Name = %s AND Id = %s'
        val = (Name, Id)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        print(result)
        if result ==('test','test',1,1) :
            return render_template('adminhome.html')
        if result is None:
            return render_template('doctor.html', dcmsg="something went wrong")
        else:
          return render_template('home.html')
    else:
        return render_template('doctor.html')


@app.route("/doctor/files", methods=["GET", "POST"])
def files():
    if request.method == "POST":
        file = request.files["file"]
        SSN = request.form["SSN"]
        radtype = request.form["rad_type"]
        filename= request.form["filename"]
        if request.files:
            sql = "INSERT INTO data (file , SSN,radtype,filename) VALUES (%s,%s, %s,%s)"
            mycursor.execute(sql, (str(file),SSN,radtype,filename ))
            mydb.commit()
        return render_template("files.html", msg="file saved")
    return render_template("files.html")


@app.route('/patient/contactus', methods=['POST', 'GET'])
def contactus():
    if request.method == 'POST':
        complains = request.form["complains"]
        sql = "INSERT INTO contactus (complains) VALUES (%s)"
        val = (complains, )
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('contactus.html', mes="complain received")
    return render_template('contactus.html')

@app.route('/patient/appointment', methods=['POST', 'GET'])
def appointment():
    if request.method == 'POST':
        Name = request.form["Name"]
        rad_type = request.form["rad_type"]
        start_date= request.form["start_date"]
        end_date= request.form["end_date"]
        sql = "INSERT INTO appointment (Name,rad_type,start_date,end_date) VALUES (%s,%s,%s,%s )"
        val = (Name,rad_type,start_date,end_date, )
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('appointment.html', mess="appointment saved")
    return render_template('appointment.html')    

@app.route('/doctor/schedual')
def scedual():
    return render_template('schedual.html')

@app.route('/doctor/admin')
def viewdoctors():
    mycursor.execute("SELECT * FROM doctors")
    row_headers=[x[0] for x in mycursor.description] #this will extract row headers
    myresult = mycursor.fetchall()
    mycursor.execute("SELECT * FROM patient")
    row_headers=[y[0] for y in mycursor.description] #this will extract row headers
    myresult1 = mycursor.fetchall()
    mycursor.execute("SELECT * FROM contactus")
    row_headers=[z[0] for z in mycursor.description] #this will extract row headers
    myresult2 = mycursor.fetchall()
    return render_template('admin.html',doctorsData=myresult ,patientData=myresult1 ,complainsData=myresult2 )


class DownloadForm(Form):
  
    download = SubmitField("results")

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
GCAL = discovery.build('calendar', 'v3', http=creds.authorize(Http()))
# "end": {"dateTime": '{}T{:d}:00:00'.format(Date, Duration), "timeZone": 'Africa/Cairo'},
EVENT = {
    'summary': 'aly',
    'start': {'dateTime': '2021-01-16T4:00:00', "timeZone": 'Africa/Cairo'},
    'end': {'dateTime': '2021-01-16T5:00:00', "timeZone": 'Africa/Cairo'},
    
}
e = GCAL.events().insert(calendarId='primary',sendNotifications=True, body=EVENT).execute()
print('''* %r event added:
    Start: %s
    End:   %s''' % (e['summary'].encode('utf-8'),
                    e['start']['dateTime'], e['end']['dateTime']))


if __name__ == '__main__':
    app.run()
