# draughtPick website and application for EE 382V, Fall 2014
# Created by Victoria Bill and Steve Rutherford
from __future__ import with_statement
import os
from datetime import datetime, timedelta
import time
import collections
from bs4 import BeautifulSoup as bs

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
import boto
#import boto.manage.cmdshell
#import paramiko



def cleanup(blob_keys):
    blobstore.delete(blob_keys)

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True)


class BeerStream(ndb.Model):
	# change for Draught Pick model
	bar_name = ndb.StringProperty()
	beer_name = ndb.StringProperty()
	brewery_name = ndb.StringProperty()
	rating = ndb.IntegerProperty()
	info = ndb.JsonProperty() 
	timestamps = ndb.StringProperty(repeated=True)


'''
def upload_file(instance, key, username, local_filepath, remote_filepath):
    """
    Upload a file to a remote directory using SFTP. All parameters except
    for "instance" are strings. The instance parameter should be a
    boto.ec2.instance.Instance object.
 
    instance        An EC2 instance to upload the files to.
    key             The file path for a valid SSH key which can be used to
                    log in to the EC2 machine.
    username        The username to log in as.
    local_filepath  The path to the file to upload.
    remote_filepath The path where the file should be uploaded to.
    """
    ssh_client = boto.manage.cmdshell.sshclient_from_instance(
        instance,
        key,
        user_name=username
    )
    ssh_client.put_file(local_filepath, remote_filepath)

# write class to test linking to AWS EC2 server
# uses boto module
# hard code an image for now
class talkAWS(webapp2.RequestHandler):
	ec2 = boto.connect_ec2()
	key_pair = ec2.create_key_pair('ec2-sample-key')  # only needs to be done once
	key_pair.save('~/Desktop')
	reservation = ec2.run_instances(image_id='ami-bb709dd2', key_name='ec2-sample-key')
	print reservation.instances
	instance = reservation.instances[0]
	print instance.state
boto ec2 example
'''

def ask_ba():
	#opener = urllib2.build_opener()
	#opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	url = 'http://beeradvocate.com/beer/profile/63/49472/'
	result = urlfetch.fetch(url, headers = {'User-Agent': 'Mozilla/5.0'}, method = urlfetch.GET)
	#page = result.read()
	soup = bs(result.content)
	return soup
 

class callSoup(webapp2.RequestHandler):
	def get(self):
		# add information to parse tesseract data later
		#	for now want to check that we can crawl beeradvocate reliably enough
		soup = ask_ba()
		print type(soup)
		print len(soup)
		print soup.title
		links = soup.find_all('a')
		print len(links)
		self.response.write('got here')


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
			template = JINJA_ENVIRONMENT.get_template('mainpage.html')
 			self.response.write(template.render(template_values))


# create new view class handler for android app, should return json dumped data of all necessary info for app
# must pass stream name in order for handler to grab for ViewSingleAndroid
class ViewAndroid(webapp2.RequestHandler):
	def get(self):
		#don't need to check for user info?
		all_streams = BeerStream.query().fetch()
		img_info = {}
		test = {}
		for x in xrange(len(all_streams)):
			stream_name = all_streams[x].stream_name
			img_info[stream_name+'_length'] = len(all_streams[x].info[stream_name]['stream_urls'])
			img_info[stream_name] = all_streams[x].info[stream_name]['stream_urls']
			test[stream_name] = str(len(all_streams[x].info[stream_name]['stream_urls']))
			for y in xrange(len(all_streams[x].info[stream_name]['stream_urls'])):
				test[stream_name] = test[stream_name] +' '+ str( all_streams[x].info[stream_name]['stream_urls'][y][0])
		print test
				
		if len(img_info) == 0:
			img_info['no_stream'] = 'no streams yet'			
		#android_data = json.dumps(img_info, sort_keys=True, separators=(',',':'))
		android_data = json.dumps(test, sort_keys=True, separators=(',',':'))
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
	('/callsoup', callSoup),
	('/viewandroid', ViewAndroid),
	('/viewsingleandroid/([^/]+)?', ViewSingleAndroid),
	('/viewnearbyandroid/([^/]+)?', ViewNearbyAndroid),
	('/uploadandroid', UploadAndroid),
	('/imageurl', UploadURL),
	('/.*', NotFoundPageHandler),
], debug=True)

