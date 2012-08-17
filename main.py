# phoneduty
# Dispatch incoming telephone voicemails/SMS messages from Twilio according to a PagerDuty on-call schedule

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import json
import logging
import urllib2
import urlparse

# Shorten MP3 URL for SMS length limits
def shorten(url):
    gurl = 'https://www.googleapis.com/urlshortener/v1/url'
    data = json.dumps({'longUrl': url})
    request = urllib2.Request(gurl, data, {'Content-Type': 'application/json'})
    try:
        f = urllib2.urlopen(request)
        results = json.load(f)
    except urllib2.HTTPError, e: # triggers on HTTP code 201
        logging.warn(e.code)
        error_content = e.read()
        results = json.JSONDecoder().decode(error_content)
    return results['id']

# Outbput TwilML to record a message and pass it to the RecordHandler
class CallHandler(webapp.RequestHandler):
    def get(self):
	logging.info('Recieved call: ' + self.request.query_string)

        # Set service key
	if (self.request.get("service_key")):
	    service_key = self.request.get("service_key")
	    logging.debug("service_key = \"" + service_key + "\"")
	else:
	    logging.error("No service key specified")

        # Set greeting
        if (self.request.get("greeting")):
            greeting = self.request.get("greeting")
            logging.debug("greeting = \"" + greeting + "\"")
        else:
            logging.info("Using default greeting")
            greeting = "Leave a message to contact the on call staff."
        
        # Determine the RecordHandler URL to use based on the current base URL
        o = urlparse.urlparse(self.request.url)
        recordURL = urlparse.urlunparse((o.scheme, o.netloc, 'record?service_key=' + service_key, '', '', ''))
	logging.debug("recordURL = \"" + recordURL + "\"")

        response = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>"
            "<Response>"
            "        <Say>" + greeting + "</Say>"
            "        <Record action=\"" + recordURL + "\" method=\"GET\"/>"
            "        <Say>I did not receive a recording.</Say>"
            "</Response>")
	logging.debug("response = \"" + response + "\"")
        self.response.out.write(response)

# Open a PagerDuty incident based on an SMS message
class SMSHandler(webapp.RequestHandler):
    def get(self):
	logging.info('Received SMS: ' + self.request.query_string)

        # Set service key
	if (self.request.get("service_key")):
	    service_key = self.request.get("service_key")
	    logging.debug("service_key = \"" + service_key + "\"")
	else:
	    logging.error("No service key specified")

        incident = '{"service_key": "%s","incident_key": "%s","event_type": "trigger","description": "%s %s"}'%(service_key,self.request.get("From"),self.request.get("From"),self.request.get("Body"))

        try:
            r = urllib2.Request("http://events.pagerduty.com/generic/2010-04-15/create_event.json", incident) #Note according to the API this should be retried on failure
            results = urllib2.urlopen(r)
            logging.debug(incident)
            logging.debug(results)
        except urllib2.HTTPError, e:
            logging.warn( e.code )
        except urllib2.URLError, e:
            logging.warn(e.reason)     

# Shorten the URL and trigger a PagerDuty incident
class RecordHandler(webapp.RequestHandler):
    def get(self):
        logging.info('Received recording: ' + self.request.query_string)

        # Set service key
	if (self.request.get("service_key")):
	    service_key = self.request.get("service_key")
	    logging.debug("service_key = \"" + service_key + "\"")
	else:
	    logging.error("No service key specified")

        recUrl = self.request.get("RecordingUrl")
        phonenumber = self.request.get("From")

        response = (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<Response><Say>Thank you. We are now directing your message to the on call staff. Goodbye.</Say>"
                "</Response>")
        self.response.out.write(response)

        if(recUrl):
	    logging.debug('Recording URL: ' + recUrl)
            recUrl = recUrl + '.mp3' # Append .mp3 to improve playback on more devices
        else:
	    logging.warn('No recording URL found')
            recUrl = ""

	shrten = "Error"
        try:
            shrten = shorten(recUrl)
        except urllib2.HTTPError, e:
            shrten = "HTTPError"
            logging.warn( e.code )
        except urllib2.URLError, e:
            shrten = "URLError"
            logging.warn(e.reason) 
        
        logging.info('Shortened to: ' + shrten)
    
        incident = '{"service_key": "%s","incident_key": "%s","event_type": "trigger","description": "%s %s"}'%(service_key,shrten,shrten,phonenumber)
        try:
            r = urllib2.Request("http://events.pagerduty.com/generic/2010-04-15/create_event.json", incident) #Note according to the API this should be retried on failure
            results = urllib2.urlopen(r)
            logging.debug(incident)
            logging.debug(results)
        except urllib2.HTTPError, e:
            logging.warn( e.code )
        except urllib2.URLError, e:
            logging.warn(e.reason)     

# A somewhat descriptive index page
class IndexHandler(webapp.RequestHandler):
    def get(self):
        response = (
                "<html>"
                "<h1>phoneduty</h1>"
		"<p><a href=\"http://www.github.com/dsshafer/phoneduty\">http://www.github.com/dsshafer/phoneduty</a></p>"
                "</html>")
        self.response.out.write(response)

app = webapp.WSGIApplication([
    ('/call', CallHandler),
    ('/record', RecordHandler),
    ('/sms', SMSHandler),
    ('/', IndexHandler)],
    debug=True)
