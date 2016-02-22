#!/usr/bin/python

#Chase's Traffic Sucks App
#Testing an update

import requests
import json
import datetime
import sys
import getopt
import time

def main(argv):
	traffic_api_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
	units = 'imperial'
	master = [] #master array of data

	api_key = ''
	origins = ''
	destinations = ''

	try:
		opts, args = getopt.getopt(argv,"hk:o:d:",["api_key=","origins=","destinations="])
	except getopt.GetoptError:
		print 'Borked: TrafficSucks.py -k <Google API Key - Required> -o <Origin(s)> -d <Destination>'
		sys.exit(2)	
	for opt, arg in opts:
		if opt == '-h':
			print 'TrafficSucks.py -k <Google API Key - Required> -o <Origin(s)> -d <Destination>'
			sys.exit()
		elif opt in ("-k", "--api_key"):
			api_key = arg
		elif opt in ("-o", "--origins"):
			origins = arg
		elif opt in ("-d", "--destinations"):
			destinations = arg

	if api_key == '':
		print 'Borked - You need a key!: TrafficSucks.py -k <Google API Key - Required> -o <Origin(s)> -d <Destination>'
		sys.exit(2)
	if origins == "":
		origins = 'Olympia, WA|Tacoma, WA|Bremerton, WA|Tanner, WA'
	if destinations == "":
		destinations = 'Seattle, WA'

	##LOOP THROUGH DATES AND TIMES

	#convert DTG to epoch for departure_time
	#Take given time and make it loop for every 30 minutes for next 2 hours (6 queries)
	count = 0
	workweek = True #check times over the entire week
	days_stillgoing = True #flag for stopping the loop

	dt_mon = 02
	dt_day = 22
	dt_startday = 22
	dt_daytext = 'Monday'
	dt_hr = 8
	dt_starthr = 8
	dt_min = 00

	while days_stillgoing: 	
		print dt_hr, ":", dt_min
		departure_time = int((datetime.datetime(2016,dt_mon,dt_day,dt_hr,dt_min) - datetime.datetime(1970,1,1)).total_seconds())

		##LOOP THROUGH traffic_model
		poss_traffic_models = ['best_guess','pessimistic'] #could include 'optomistic' but I'm not, so...

		for ptm in poss_traffic_models:
			traffic_model = ptm

			##EXECUTE QUERY

			payload = {
				'origins': origins, 
				'destinations': destinations,
				'key': api_key, 
				'departure_time': departure_time,
				'traffic_model': traffic_model,
				'units': units
			}
			#print payload
			r = requests.get(traffic_api_url, params=payload)
			#print r.url
			#print r.text
			#Need to work on error handling
			#if r.status_code == 200 :
			#	print('Error!')
			data = json.loads(r.text)
			if data['status'] != "OK":
				print ('There was an error from Google\'s API. Please try again.')
				sys.exit()
			#print data
			#getsgoofy parsing deep arrays; there has to be a better way to do this
			current = 0
			while current < len(data['rows']):
				currow = data['rows'][current]
				currow_ctr = 0
				while currow_ctr < len(currow['elements']):
					curelement = currow['elements'][currow_ctr]
					#print curelement
					traveldtg = time.strftime('%A at %H:%M',  time.gmtime(departure_time))
					#Calc the delta
					curdelta = curelement['duration_in_traffic']['value'] - curelement['duration']['value']
					master.append([
						data['origin_addresses'][current],
						data['destination_addresses'][current],
						traveldtg,
						curelement['duration']['text'],
						curelement['duration']['value'],
						curelement['duration_in_traffic']['text'],
						curelement['duration_in_traffic']['value'],
						curelement['distance']['text'],
						curelement['distance']['value'],
						ptm,
						curdelta
						])
					currow_ctr += 1
				current += 1

		#Bounce between 30 and 00
		if dt_min == 00:
			dt_min = 30
		else:
			dt_min = 00
			dt_hr += 1

		if workweek:
			if (dt_hr - dt_starthr) == 2: #We've gone our 5 rounds
				if (dt_day - dt_startday) == 5: #we've done five days, and all the hours on the 5th day
					days_stillgoing = False
				else:
					dt_day = dt_day +1
					dt_hr = dt_starthr
		#workweek = True #check times over the entire week
		#days_done = False #flag for stopping the loop

		#dt_mon = 02
		#dt_day = 22
		#dt_daytext = 'Monday'
		#dt_hr = 8
		#dt_min = 00
		count += 1
		if count == 10: #Cap the queries
			days_stillgoing = False
	#print master

	for disp_rows in master:
		print_traveltime = str(disp_rows[2])
		print_origin = str(disp_rows[0])
		print_dest = str(disp_rows[1])
		print_timebest = str(disp_rows[3])
		print_timetraffic = str(disp_rows[5])
		print_dist = str(disp_rows[7])
		print_ptm = str(disp_rows[9])
		print_delta = str(disp_rows[10])
		print "When traveling on ", print_traveltime.strip()," from ", print_origin.strip(), " to " , print_dest.strip(), ", Google estimates it will take between ",print_timebest.strip()," and ",print_timetraffic.strip(),", over a distance of ",print_dist.strip()," (",print_ptm.strip(),", delta: ", print_delta.strip(),")."

	#This sorts master, currently by the fastest duration_in_traffic value
	def getkey(item):
		return item[6]
	master_fastest = sorted(master, key=getkey)
	#print master_fastest[0]

if __name__ == "__main__":
	main (sys.argv[1:])
