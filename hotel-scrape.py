#!/usr/bin/env python3

"""
A python script for getting information from hotels on https://www.woodspring.com
This script will get: Name, Location, Price, and TripAdvisor rating then put it into a csv file

Uses:
	-selenium for website rendering
	-bs4 for html parsing
	-threading to be fast
"""

# Import modules to make requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
# Start Parsing with BS4
from bs4 import BeautifulSoup
# threading
from multiprocessing.dummy import Lock
from multiprocessing.dummy import Process
# file handling
import os

def get_hotel_info_from_html(lock,hotel):
	info = hotel.find("div",{"class":"hotel-details"})
	obj = {}
	obj["name"] = info.find("div",{"class":"hotel-name"}).text[1:]
	# print("Getting information for {}".format(obj["name"]))
	obj["location"] = info.find("div",{"class":"hotel-address ng-binding"}).text
	price = hotel.find("div",{"class":"currency ng-binding"}).text # Currency
	price += hotel.find("div",{"class":"price-whole ng-binding"}).text + "." # Left of decimal
	price += hotel.find("div",{"class":"price-fraction ng-binding"}).text # Right of decimal
	obj["price"] = price
	try:
		frequency = hotel.find("div",{"class":"nightly-rate ng-binding"}).text
	except AttributeError:
		frequency = hotel.find("div",{"class":"weekly-rate ng-binding"}).text
	obj["frequency"] = frequency
	obj["rating"] = info.find("div",{"class":"ta-rating"}).findChildren()[0]['alt']
	
	# print("entering write stage...")
	write_to_csv(lock,obj)

	return

def write_to_csv(lock,obj,filename="data.csv"):
	lock.acquire()
	header = "name,location,price,frequency,rating"
	try:
		if os.path.exists(filename):
			f = open(filename,"a")
			print("appending")
		else:
			print("making header and writing")
			f = open(filename,"w+")
			f.write(header + "\n")

	
		for column in header.split(","):
			f.write('"'+obj[column]+'"'+",")
		# Next 2 lines will remove the last "," since it's the last thing in the file
		f.seek(f.tell() - 1, os.SEEK_SET)
		f.truncate()
		# Add newline
		f.write("\n")
	finally:
		f.close()
		lock.release()

__author__ = "Cody Wolter"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Cody Wolter"
__email__ = "cwolter97@gmail.com"
__status__ = "Production"

def main():
	BASE_URL = "https://www.woodspring.com"
	# Page renderer initialization
	options = Options()
	options.add_argument("--headless")
	driver = webdriver.Firefox(firefox_options=options)

	# Get page
	print("[Opening Web Page]")
	driver.get(BASE_URL+"/locations")
	html_doc = driver.page_source

	soup = BeautifulSoup(html_doc, 'html.parser')
	section = soup.find("section", {"class":"ws-locations-list-section"})
	states = section.find_all("div", {"class":"subdiv-name"})

	state_links = list()
	for state in states:
		state_links.append(state.find("a")['href'])

	print("[WORKING]")
	x = 0
	for link in state_links:
		x+=1
		print("STATE: {:<2}/{:<2}".format(x,len(state_links)))
		driver.get(BASE_URL+link)

		hotel_list_html = driver.page_source
		hotel_soup = BeautifulSoup(hotel_list_html, 'html.parser')
		hotel_list = hotel_soup.find_all("div",{"class":"list-view ng-scope"})
		
		lock = Lock()
		y = 0
		for hotel in hotel_list:
			y += 1
			# print("HOTEL: {:<2}/{:<2}".format(y,len(hotel_list))) # Uncomment for more spam saying all hotels are being ran
			Process(target=get_hotel_info_from_html, args=(lock,hotel)).start()

	print("Success!")

if __name__ == "__main__":
	main()
