# draughtPick website and application for EE 382V, Fall 2014
# Created by Victoria Bill and Steve Rutherford
from __future__ import with_statement
import os
from datetime import datetime, timedelta
import time
import collections
from bs4 import BeautifulSoup as bs
import urllib2
from random import choice

from google.appengine.api import users
from google.appengine.api import mail, images, files
from google.appengine.ext import ndb
from google.appengine.ext import blobstore, deferred
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import urlfetch

import jinja2
import webapp2
import re
import json

def cleanup(blob_keys):
    blobstore.delete(blob_keys)

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True)


# different user agents to use to keep from being banned.
user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0.1) Gecko/20100101 Firefox/8.0.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19'
]


class Vendors(ndb.Model):
	# change for Draught Pick model
	location = ndb.StringProperty()
	vendor_name = ndb.StringProperty()
	breweries = ndb.StringProperty(repeated=True)
	ratings = ndb.IntegerProperty(repeated=True)
	beer_info = ndb.JsonProperty() 
	timestamps = ndb.StringProperty(repeated=True)
	# ! want to store beer advocate beer id and brewery id
	# format is url/beer/profile/brew#/beer#/
	# beer style is also an id number
	# /beer/style/152 is English Barleywine


class BeerData(ndb.Model):
	brewery = ndb.StringProperty()
	beer = ndb.StringProperty()
	rating = ndb.StringProperty()
	abv = ndb.StringProperty()
	btype = ndb.StringProperty()
	style_id = ndb.StringProperty()
	beer_id = ndb.StringProperty()


def ask_ba(id_num):
	#opener = urllib2.build_opener()
	#opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	url = 'http://beeradvocate.com/beer/profile/' + id_num
	#result = urlfetch.fetch(url, headers = {'User-Agent': 'Mozilla/5.0'}, method = urlfetch.GET)
	#page = result.read()
	#soup = bs(result.content)
	version = choice(user_agents)
	headers = { 'User-Agent' : version }
	req = urllib2.Request(url, None, headers)
	htmlText = urllib2.urlopen(req).read()
 	soup = bs(htmlText)
	return soup


class callSoup(webapp2.RequestHandler):
	def get(self):
		# add information to parse tesseract data later
		#	for now want to check that we can crawl beeradvocate reliably enough
		id_num = self.request.get_all('id_number')[0]
		if BeerData.query(BeerData.beer_id==id_num).fetch():
			print "already have this one"
			self.redirect('/')
		else:
			soup = ask_ba(id_num)
			print type(soup)
			print len(soup)
			print soup.title
			style = []
			for link in soup.find_all('a'):
				if link.get('href'):
					if 'style' in link.get('href'):
						style.append(link)
						abv_text = link.nextSibling
						break
			abv_str = abv_text.string.replace(u'\xa0', u' ')
			abv = abv_str.split(' ')[3]
			beer_style = str(style[0]).split('>')[2].split('<')[0]
			style_id = str(style[0]).split('/')[3]
			rating_text = 'BAscore_big ba-score'
			span = soup.find_all('span', {'class': rating_text})
			ba_rating = span[0].string
			title_text = 'titleBar'
			title = soup.find_all('div', {'class': title_text})
			title = str(title[0])
			beer_name = title.split('<')[2].split('>')[1]
			brewery_name = title.split('<')[3].split('- ')[1]
			print beer_name
			print brewery_name
			print ba_rating
			print beer_style
			print style_id
			print abv
			beer_data = BeerData(brewery=brewery_name, beer=beer_name, rating=ba_rating, abv=abv, btype=beer_style, style_id=style_id, beer_id=id_num)
			beer_key = beer_data.put()
			time.sleep(0.1)
			self.redirect('/')

class Create(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url = users.create_logout_url('/')
			url_linktext = 'Logout'
			template_values = {
			'url': url,
 			'url_linktext': url_linktext,
 			}
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
			template_values = {
				'url': url,
 				'url_linktext': url_linktext,
 			}

		template = JINJA_ENVIRONMENT.get_template('create.html')
 		self.response.write(template.render(template_values))


class MainPage(webapp2.RequestHandler):
	#main page = login, should check for login then dump to manage page?
  def get(self):
		user = users.get_current_user()
		if user:
			greeting = ('Welcome, %s!' % (user.nickname()))
			url = users.create_logout_url('/')
			url_linktext = 'Logout'
			template_values = {
 			'greeting': greeting,
			'url': url,
 			'url_linktext': url_linktext,
 			}
			all_beers = BeerData.query().fetch()
			print all_beers
			template = JINJA_ENVIRONMENT.get_template('mainpage.html')
 			self.response.write(template.render(template_values))
		else:
			greeting = 'Sign in or register:'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
			template_values = {
 				'greeting': greeting,
				'url': url,
 				'url_linktext': url_linktext,
 			}
			template = JINJA_ENVIRONMENT.get_template('index.html')
 			self.response.write(template.render(template_values))


# create new view class handler for android app, should return json dumped data of all necessary info for app
# must pass stream name in order for handler to grab for ViewSingleAndroid
class BeerDataAndroid(webapp2.RequestHandler):
	def get(self):
		#don't need to check for user info?
		all_beers = BeerData.query().fetch()
		print 'get all beer data'
		beer_info = {}
		for x in xrange(len(all_beers)):
			# create build_dict function for this?
			beer_info[all_beers[x].beer] = {}
			beer_info[all_beers[x].beer]['rating'] = all_beers[x].rating
			beer_info[all_beers[x].beer]['brewery'] = all_beers[x].brewery
			beer_info[all_beers[x].beer]['abv'] = all_beers[x].abv
			beer_info[all_beers[x].beer]['beer_type'] = all_beers[x].btype
					
		print beer_info		
		if len(beer_info) == 0:
			beer_info['no_data'] = 'no beer data yet'			
		#android_data = json.dumps(img_info, sort_keys=True, separators=(',',':'))
		android_data = json.dumps(beer_info, sort_keys=True, separators=(',',':'))
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(android_data)
		webapp2.Response(android_data)

		
	
class ViewSingleAndroid(webapp2.RequestHandler):
	# android needs to pass in stream_name in url for view single
	def get(self, stream_name):
		#don't need to check for user info?
		single_stream = BeerStream.query(BeerStream.stream_name == stream_name).fetch()
		single_stream[0].info[stream_name]['views'] += 1
		single_stream[0].timestamps.append(str(datetime.now()))
		single_stream[0].put()
		img_info = {}
		test = {}
		for x in xrange(len(single_stream)):
			img_info[single_stream[x].stream_name] = single_stream[x].info
			test[stream_name] = str(len(single_stream[x].info[stream_name]['stream_urls']))
			for y in xrange(len(single_stream[x].info[stream_name]['stream_urls'])):
				test[stream_name] = test[stream_name] +' '+ str( single_stream[x].info[stream_name]['stream_urls'][y][0])
		if len(img_info) == 0:
			img_info['no_stream'] = 'no streams yet'	
		
		android_data = json.dumps(test, sort_keys=True, separators=(',',':'))
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(android_data)
		webapp2.Response(android_data)
		

class ViewNearbyAndroid(webapp2.RequestHandler):
	# android needs to pass in location for view nearby????
	def get(self, location):
		#don't need to check for user info?
		#query should then check location and get locations where difference is less than some_distance
		#calculate abs distance from latitude and longitude?
		nearby_streams = BeerStream.query().fetch()
		img_info = {}
		test = {}
		for x in xrange(len(nearby_streams)):
			img_info[nearby_streams[x].stream_name] = nearby_streams[x].info
			test[stream_name] = str(len(nearby_streams[x].info[stream_name]['stream_urls']))
			for y in xrange(len(nearby_streams[x].info[stream_name]['stream_urls'])):
				test[stream_name] = test[stream_name] +' '+ str( nearby_streams[x].info[stream_name]['stream_urls'][y][0])
		if len(img_info) == 0:
			img_info['no_stream'] = 'no streams yet'	
		
		android_data = json.dumps(test, sort_keys=True, separators=(',',':'))
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(android_data)
		webapp2.Response(android_data)


# create new upload handler for android app, should accept full image from app? store to blobstore as before?
class UploadAndroid(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		print "entered android upload"
		#can the android app pass the entire image?
		#look at android camera code to see how upload/image compression and storing is handled
		#how to get stream name?
		stream_name = 'phone_uploads'
		print stream_name		
		upload_files = self.get_uploads('file')	
		blob_info = upload_files[0]
		upload_time = datetime.now()
		single_stream = BeerStream.query(BeerStream.stream_name == stream_name).fetch()
		single_stream[0].info[stream_name]['stream_urls'].append((images.get_serving_url(blob_info.key()), str(upload_time.date())))
		single_stream[0].info[stream_name]['stream_len'] += 1
		single_stream[0].put()
		time.sleep(0.1)
		self.response.write(images.get_serving_url(blob_info.key()))

class UploadURL(webapp2.RequestHandler):
	#clicking on view tab should take you to view all streams page
	def get(self):
		# the create page (or view single/image upload) serves as the MainHandler for the create stream UploadHandler, ServeHandler
		upload_url = blobstore.create_upload_url('/uploadandroid')
		url_data = json.dumps({'uploadURL':upload_url})
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(url_data)
		webapp2.Response(url_data)

class NotFoundPageHandler(webapp2.RequestHandler):
	def get(self):
		self.error(404)
		user = users.get_current_user()
		if user:
			url = users.create_logout_url('/')
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		template_values = {
      'url': url,
      'url_linktext': url_linktext,
  	}
		template_values['error_msg'] = 'Error: you attempted to reach a stream or page that does not exist. '
		
		template = JINJA_ENVIRONMENT.get_template('error.html')
		self.response.write(template.render(template_values))	



application = webapp2.WSGIApplication([
  ('/', MainPage),
	('/create', Create),
	('/callsoup', callSoup),
	('/getbeer', BeerDataAndroid),
	('/viewsingleandroid/([^/]+)?', ViewSingleAndroid),
	('/viewnearbyandroid/([^/]+)?', ViewNearbyAndroid),
	('/uploadandroid', UploadAndroid),
	('/imageurl', UploadURL),
	('/.*', NotFoundPageHandler),
], debug=True)

