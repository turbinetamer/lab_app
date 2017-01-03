from flask import Flask, request, render_template
import time
import datetime


app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

@app.route("/")
def hello():
    return "Hello World!-from lab_app.py"

@app.route("/lab_temp")
def lab_temp():
	#import sys
	#import Adafruit_DHT
	#humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
	#if humidity is not None and temperature is not None:
	#	return render_template("lab_temp.html",temp=temperature,hum=humidity)
	#else:
	#	return render_template("no_sensor.html")
	import time, logging, math
	import Adafruit_GPIO as GPIO
	import Adafruit_GPIO.SPI as SPI
	import Adafruit_MAX31855.MAX31855 as MAX31855
	
	SPI_PORT = 0
	SPI_DEVICE = 0
	sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=5000000))
	
	temp = sensor.readTempC()
	internal = sensor.readInternalC()
	print temp,internal
	
	if temp is not None and internal is not None:
		return render_template("lab_temp.html", d_temp=temp, d_int=internal)
		#return "We Have Data!"
		#return 'Temp=%0.1f  Internal=%0.1f'%(temp,internal)
	else:
		#return render_template("no_sensor.html")
		return "Sorry, No Data"
		

@app.route("/lab_env_db", methods=['GET']) 
def lab_env_db():
	temperatures, humidities, from_date_str, to_date_str = get_records()
	
	#return 
	#return "lab_env_db from %s to %s  items=%d last row %s " % (from_date_str, to_date_str, len(temperatures), temperatures[len(temperatures)-1])
	#return render_template("lab_env_db.html",temp=temperatures,hum=humidities)
	return render_template("lab_env_db.html",temp 	= temperatures, 
											 hum= humidities,
											 from_date = from_date_str,
											 to_date = to_date_str,
											 temp_items = len(temperatures),
											 hum_items = len(humidities))

def get_records():
	from_date_str 	= request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
	to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
	range_h_form	= request.args.get('range_h','');  #This will return a string, if field range_h exists in the request

	range_h_int 	= "nan"  #initialise this variable with not a number
	dlist = {"from_date_str":from_date_str,
				"to_date_str":to_date_str,
				"range_h_form":range_h_form}
				
	for key in dlist:
		print(key,dlist[key])
	
	try: 
		range_h_int	= int(range_h_form)
	except:
		print "range_h_form still not a number, too bad"

	if not validate_date(from_date_str):			# Validate date before sending it to the DB
		from_date_str 	= time.strftime("%Y-%m-%d 00:00")
	if not validate_date(to_date_str):
		to_date_str 	= time.strftime("%Y-%m-%d %H:%M")		# Validate date before sending it to the DB

		# If range_h is defined, we don't need the from and to times
	if isinstance(range_h_int,int):	
		time_now		= datetime.datetime.now()
		time_from 		= time_now - datetime.timedelta(hours = range_h_int)
		time_to   		= time_now
		from_date_str   = time_from.strftime("%Y-%m-%d %H:%M")
		to_date_str	    = time_to.strftime("%Y-%m-%d %H:%M")

	for key in dlist:
		print(key,dlist[key])
	
	import sqlite3
	conn=sqlite3.connect('/var/www/lab_app/lab_app.db')
	curs=conn.cursor()
	t_cmd = "SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str)
	print("t_cmd ",t_cmd)
	curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	temperatures 	= curs.fetchall()
	ok_temps=[]							# validate database records
	for row in temperatures:
		if row[2] == None:
			print(row)					# log error records
		else:
			ok_temps.append(row)
	temperatures = ok_temps
	
	c_cmd = "SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str)
	print("c_cmd ",c_cmd)
	curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	humidities 		= curs.fetchall()
	ok_humids=[]							# validate database records
	for row in humidities:
		if row[2] == None:
			print(row)					# log error records
		else:
			ok_humids.append(row)
	humidities = ok_humids
	
	conn.close()
	return [temperatures, humidities, from_date_str, to_date_str]

def validate_date(d):
	try:
		datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
		return True
	except ValueError:
		return False

if __name__ == "__main__":
#	print "Starting __main__"
	app.run(host='0.0.0.0', port=8080)
	