#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
from datetime import date
from xml.etree import ElementTree as ET
import os
# from random import sample
import random
import json
import copy
# import os
# import json
# import logging

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

# booking_id_secret = None
# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
# 	booking_id_secret = (json.load(data_file))['booking_id']



REF_API = 'api'
REF_CLIENT = 'client'
REF_AGENT = 'agent'

CONFIRMED = 'Confirmed or Completed'

bad_hotels = [{"city_code": "SHEN", "item_code": "ASC"}, 
				{"city_code": "CHEG", "item_code": "HOW"},
				{"city_code": "WUH", "item_code": "CIT"},
				{"city_code": "CKG", "item_code": "94"}
				]

def is_bad_hotel(city_code, item_code):
	for bad_hotel in bad_hotels:
		if bad_hotel['city_code'] == city_code and bad_hotel['item_code'] == item_code:
			return True
	return False

def dump_csv(res, output_filename, from_date):
	keys = res[0].keys()
	final_output_filename = '_'.join(['Output_search_item_hr', 
										output_filename, 
										from_date.strftime('%y%m%d'), 
										datetime.datetime.now().strftime('%H%M')
										]) + '.csv'
	# with open('output_Search_booking_id_' + from_date.strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '_' + str(duration) + 'd.csv', 'w', newline='', encoding='utf-8') as output_file:
	with open(final_output_filename, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

@click.command()
@click.option('--filename', default='output_SearchItemHR_170718_1722.csv')
@click.option('--client', default='ctrip')
@click.option('--output', default='ctrip_email')
# @click.option('--days', default=1, type=int)
def searh_item_hr_ctrip(filename, client, output):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	pp = pprint

	agent_secret = None
	with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
		# agent_secret = (json.load(data_file))[client]
		agent_secret = json.load(data_file)

	# validate_d(from_d)
	# validate_d(to_d)

	# from_date = datetime.datetime.today().date() + datetime.timedelta(days=days)
	# to_date = from_date + datetime.timedelta(days=1)

	print('Search client.. ' + client)
	# print('Duration.. ' + )

	# from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	# to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	# pp.pprint('? ' + str(skip))

	bookings = []
	res = []
	# filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
	with open(filename, encoding='utf-8-sig') as csvfile:
		ids = set()
		reader = csv.DictReader(csvfile)
		for row in reader:
			# pp.pprint(row['hotel_id'])
			if row['gta_api_booking_id'] not in ids:
				entry = dict()
				entry['client_booking_id'] = row['client_booking_id']
				entry['agent_booking_id'] = row['agent_booking_id']
				entry['gta_api_booking_id'] = row['gta_api_booking_id']
				entry['booking_status'] = row['booking_status']
				entry['booking_creation_date'] = row['booking_creation_date']
				entry['booking_departure_date'] = row['booking_departure_date']
				entry['booking_name'] = row['booking_name']
				entry['booking_net_price'] = row['booking_net_price']
				entry['booking_currency'] = row['booking_currency']
				entry['hotel_confirmation_#'] = ''
				entry['hotel_confirmation_status'] = ''
				entry['client_name'] = ''
				if 'client_name' in row:
					entry['client_name'] = row['client_name']
				if 'hotel_confirmation_#' in row:
					entry['hotel_confirmation_#'] = row['hotel_confirmation_#']
				if 'hotel_confirmation_status' in row:
					entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
				bookings.append(entry)
			ids.add(row['gta_api_booking_id'])

	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchBookingItemRequest.xml'))
	# search_tree.find('.//RequestorID').set('Client', agent_secret['id'])
	# search_tree.find('.//RequestorID').set('EMailAddress', agent_secret['email'])
	# search_tree.find('.//RequestorID').set('Password', agent_secret['password'])

	for counter, booking in enumerate(bookings):
		pp.pprint('Searching booking id: ' + str(counter) + ': ' + booking['gta_api_booking_id'])

		if 'client_name' not in booking.keys():
			print('Error: No client name...')
			continue

		search_tree.find('.//RequestorID').set('Client', agent_secret[booking['client_name']]['id'])
		search_tree.find('.//RequestorID').set('EMailAddress', agent_secret[booking['client_name']]['email'])
		search_tree.find('.//RequestorID').set('Password', agent_secret[booking['client_name']]['password'])

		if not booking['hotel_confirmation_#'] and booking['hotel_confirmation_#'] != '':
			print('have hotel confirmation # already.. skipping')
			entry = copy.deepcopy(booking)
			res.append(entry)
			continue
		if not booking['hotel_confirmation_status'] and booking['hotel_confirmation_status'] != '':
			print('status updated already.. skipping')
			entry = copy.deepcopy(booking)
			res.append(entry)
			continue	

		if CONFIRMED not in booking['booking_status']:
			print('Booking not confirmed.. skipping..')
			continue
		# search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
		# search_tree.find('.//ItemCode').text = hotel_code['item_code']
		booking_id = booking['gta_api_booking_id'].replace('041/', '')
		for search_request in search_tree.find('.//RequestDetails'):
			search_request.find('.//BookingReference').text = booking_id

		try:
			r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
		except OSError:
			pp.pprint('Error: OSError.. Searching has stopped..')
			continue

		r_tree = ET.fromstring(r.text)

		items_ele = r_tree.find('.//BookingItems')
		if items_ele == None:
			print('Error: No BookingItems found..')
			continue

		for booking_item in r_tree.find('.//BookingItems'):
			hotel_ref_ele = booking_item.find('.//ItemConfirmationReference')
			if hotel_ref_ele != None:
				booking['hotel_confirmation_#'] = hotel_ref_ele.text

			# logic to exclude bad hotels
			city_ele = booking_item.find('.//ItemCity')
			item_ele = booking_item.find('.//Item')
			if city_ele != None and items_ele != None:
				city_code = city_ele.get('Code')
				item_code = item_ele.get('Code')
				
				if is_bad_hotel(city_code, item_code):
					print('Warning: bad hotel.. skipping.. ')
					continue

			entry = copy.deepcopy(booking)
			res.append(entry)

	dump_csv(res, output, datetime.datetime.today().date())

	# # keys = res[0].keys()
	# keys = res[0].keys()
	# # with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	# with open('output_Search_item_hr_' + datetime.datetime.today().date().strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
	# 	dict_writer = csv.DictWriter(output_file, keys)
	# 	dict_writer.writeheader()
	# 	dict_writer.writerows(res)
	

if __name__ == '__main__':
	searh_item_hr_ctrip()