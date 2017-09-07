#!/usr/bin/env python
# coding=utf-8

import pprint
# import csv
import click 
# import requests
# import datetime as datetime
# from datetime import date
# from xml.etree import ElementTree as ET
import os
# from random import sample
# import random
# import json
# import logging
import subprocess
import glob
import time
import sys
import datetime
import re

@click.command()
@click.option('--days', default=24, type=int)
@click.option('--duration', default=0, type=int)
@click.option('--output', default='ctrip_email')
# @click.option('--days', default=1, type=int)
def ctripref_email(days, duration, output):

	# python booking_id.py --days 0 --duration 0 --client ctrip --d_type departure
	# subprocess.call(['python', 'booking_id.py', '--days', str(days), '--duration', str(duration), '--client', 'ctrip', '--d_type', 'departure'])
	# subprocess.call(['python', 'booking_id_ctrip.py', '--days', str(days), '--duration', str(duration), '--d_type', 'departure'])
	subprocess.call(['python', 'booking_id_ctripplus.py', 
									'--days', str(days), 
									'--duration', str(duration), 
									'--d_type', 'departure', 
									'--output', output
									])

	for i in range(3):
		print('sleeping.. ctrip')
		time.sleep(1)

	target_filename = '_'.join([ 'Output_search_booking_id',
									output
								]) + '*.csv'

	# newest = max(glob.iglob('Output_search_booking_id_*.csv'), key=os.path.getctime)
	newest = max(glob.iglob(target_filename), key=os.path.getctime)
	subprocess.call(['python', 'search_item_hr_ctrip.py', 
									'--filename', newest,
									'--output', output
									])

	for i in range(3):
		print('sleeping..')
		time.sleep(1)

	target_filename = '_'.join([ 'Output_search_item_hr',
									output
								]) + '*.csv'

	# newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	newest = max(glob.iglob(target_filename), key=os.path.getctime)
	subprocess.call(['python', 'hc_ctrip.py', 
								'--filename', newest,
								'--output', output
								])

	for i in range(3):
		print('sleeping..')
		time.sleep(1)

	# newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	# subprocess.call(['python', 'sendmail.py', '--filename', 'output_hotel_ref_*.csv', '--title', 'Ctrip_hotel_ref'])

	# newest = max(glob.iglob('output_hotel_ref_*.csv'), key=os.path.getctime)

	# today_date = datetime.datetime.now().strftime('%y%m%d')
	# try:
	# 	newest_date = re.search('output_hotel_ref_(\d+)', newest).group(1)
	# except AttributeError:
	# 	newest_date = ''
	# if newest_date != today_date:
	# 	print('Error: newest date != today date.. mannual intervention needed..')
	# 	return

	# print('newest date: ' + newest_date)

	# while True:
	# 	sys.stdout.write("Would you like to proceed to call Ctrip's update hotel res no API? " + newest + " [Y/N]")
	# 	choice = input().lower()
	# 	if choice == 'y' or choice == 'yes':
	# 		break
	# 	if choice == 'n' or choice == 'no':
	# 		return

	subprocess.call(['python', 'sendmail_win_ctrip.py', 
									'--output', output
									])


if __name__ == '__main__':
	ctripref_email()