
import cookielib
import logging
import re
import urllib
import urllib2

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class Message(object):
	def __init__(self, client, message_id, **kwargs):
		self.client = client
		self.message_id = message_id
		for key, value in kwargs.iteritems():
			setattr(self, '_%s' % key, value)

	def __str__(self):
		return ("%s (%s)" % (self.subject or "", self.message_id)).strip()

	def __unicode__(self):
		return str(self)

	@property
	def soup_message(self):
		if not hasattr(self, '_soup_message'):
			endpoint = Client.ENDPOINT_MESSAGE_VIEW % self.message_id
			html = self.client._request(endpoint)
			self._soup_message = BeautifulSoup(html)
		return self._soup_message

	@property
	def from_(self):
		if not hasattr(self, '_from_'):
			raise NotImplementedError("_from_")
		return self._from_

	@property
	def subject(self):
		if not hasattr(self, '_subject'):
			self._subject = self.soup_message.find(class_='email_subject').get_text()
		return self._subject

	@property
	def datetime(self):
		if not hasattr(self, '_datetime'):
			raise NotImplementedError("_datetime")
		return self._datetime

	@property
	def content(self):
		if not hasattr(self, '_content'):
			self._content = self.soup_message.find(id='email_message_content').get_text()
		return self._content


class Client(object):
	BASE_URL = 'https://imentor.imentorinteractive.org'
	ENDPOINT_MESSAGE_LIST = 'message/list/'
	ENDPOINT_MESSAGE_VIEW = 'message/view/%s/'

	def __init__(self, email, password):
		self._logged_in = False
		self.email = email
		self.password = password

	def login(self):
		logger.info("Logging in...")
		# Build opener
		cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		# Open old URL to get session
		self.opener.open(Client.BASE_URL)
		# Actually POST to login
		params = {'email': self.email, 'password': self.password}
		data = urllib.urlencode(params)
		self.opener.open(Client.BASE_URL, data)
		self._logged_in = True
		logger.info("Logged in")

	def _request(self, endpoint):
		if not self._logged_in:
			self.login()
		url = "%s/%s" % (Client.BASE_URL, endpoint)
		return self.opener.open(url).read()

	def get_messages(self):
		html = self._request(Client.ENDPOINT_MESSAGE_LIST)
		soup = BeautifulSoup(html)
		results = []
		rows = soup.find_all('tr', class_='row')
		for row in rows:
			link = row.find('a')
			if not link:
				continue
			href = link.get('href')
			# Message links:
			# /message/view/12345/
			match = re.match(r"/message/view/(\d+)/", href)
			if not match:
				continue
			message_id = match.groups()[0]
			from_ = row.find(class_='from-name').get_text()
			subject = link.get_text()
			columns = row.find_all('td')
			datetime = columns and columns[-1].get_text()
			message = Message(self,
							  message_id,
							  from_=from_,
							  subject=subject,
							  datetime=datetime)
			results.append(message)
		return results

	def get_message(self, message_id):
		return Message(self, message_id)
