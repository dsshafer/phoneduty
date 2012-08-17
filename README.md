phoneduty
=========
Dispatch incoming telephone voicemails/SMS messages from Twilio according to a PagerDuty on-call schedule

Based on sample code published in February 2012 by David Hayes (see [Triggering an alert from a phone call (code sample)](http://blog.pagerduty.com/2012/02/triggering-an-alert-from-a-phone-call-code-sample/))

Overview
--------
Uses [Google App Engine](http://appengine.google.com) with [PagerDuty](http://www.pagerduty.com) for on-call scheduling and [Twilio](http://www.twilio.com) for telephone/SMS handling.

This version improves upon the sample code in a few ways:

* Added support for SMS messages
* Added support for multiple on-call numbers by passing the PagerDuty API key and voicemail greeting in the GET request
* Updated to Python 2.7 and webapp2
* Updated to use the full Google URL Shortener API

Requirements
------------
1. PagerDuty account: [http://www.pagerduty.com](http://www.pagerduty.com)
2. Twilio account: [http://www.twilio.com](http://www.twilio.com)
3. Google App Engine account: [http://appengine.google.com](http://appengine.google.com)
4. Google App Engine SDK for Python: [https://developers.google.com/appengine/downloads](https://developers.google.com/appengine/downloads)

Usage
-----
The phoneduty application is configured in Twilio as a TwiML app to handle incoming telephone calls or SMS messages to a Twilio phone number.

### Receive voice call:

<code>GET http://{appname}.appspot.com/call?service\_key={service\_key}(&greeting={greeting})</code>

Return TwiML instructing Twilio to speak a greeting to the caller and record a message. If the caller leaves
a message, generate a PagerDuty incident for the service identified by
`service_key`. The incident will contain the caller's phone number and a
shortened link to the recording.

Example:

<code>GET http://example.appspot.com/call?service\_key=1234567890abcdef1234567890abcdef&greeting=Leave+a+message+to+contact+the+server+administrator+on+call

### Receive SMS message:
<code>GET http://{appname}.appspot.com/sms?service\_key={service\_key}</code>

Generate a PagerDuty incident for the service identified by `service_key`.
The incident will contain the sender's phone number and the SMS text.

Example:

<code>GET http://example.appspot.com/sms?service\_key=1234567890abcdef1234567890abcdef</code>

### Options

#### service\_key

PagerDuty service API key; a 32-digit hexadecimal string corresponding to a PagerDuty service created using
the "Generic API system" service type.

Example:

<code>service\_key=1234567890abcdef1234567890abcdef</code>

#### greeting

A URL-encoded text greeting to be spoken by Twilio. If not specified, the default greeting
is "Leave a message to contact the on call staff."

Example:

<code>greeting=Leave+a+message+to+contact+the+server+administrator+on+call.</code>

Deployment
----------
1. Create a new Google App Engine application, and remember the application name; example: **example.appspot.com**

2. Edit `app.yaml` and change "new-project-template" to your application name, then upload the application using `appcfg.py update` (see [Uploading, Downloading, and Managing a Python App](https://developers.google.com/appengine/docs/python/tools/uploadinganapp))

3. Create a new PagerDuty service using the "Generic API system" service type; note the resulting 32-digit hexadecimal Service API key; example: **1234567890abcdef1234567890abcdef**

4. In Twilio, create a new TwiML App (see [Create App](https://www.twilio.com/user/account/apps/add))

5. Change the Voice request type for the new app from `POST` to `GET`

6. Set the Voice request URL to your application for receiving voice calls, for example (remember to replace "example" with your application name, and service\_key with your PagerDuty service API key):

    <code>http://example.appspot.com/call?service\_key=1234567890abcdef1234567890abcdef</code>

7. Change the SMS request type from `POST` to `GET`

8.  Set the SMS request URL to your application for receiving SMS messages, for example (remember to replace "example" with your application name, and service\_key with your PagerDuty service API key):

    <code>http://example.appspot.com/sms?service\_key=1234567890abcdef1234567890abcdef</code>

9. Try calling your application using the Twilio Client and verify it creates a PagerDuty incident successfully.

10. In Twilio, create a new number and associate it with your application for Voice and SMS.

11. For additional on-call numbers, use the same Google App Engine application, but specify a new PagerDuty service, TwiML app, and Twilio number.

### Example: Multiple Phone Numbers

#### Google App Engine Application
* example.appspot.com (phoneduty application)

#### PagerDuty Services
* "Server Administrators Telephone (555-555-0111)" (Service API key: 11111111111111111111111111111111)
* "Database Administrators Telephone (555-555-0122)" (Service API key: 22222222222222222222222222222222)

#### Twilio TwiML Apps

##### Server Administrators App

Voice:

<code>GET http://example.appspot.com/call?service\_key=11111111111111111111111111111111&greeting=Leave+a+message+to+page+the+server+administrator+on+call</code>

SMS:

<code>GET http://example.appspot.com/sms?service\_key=11111111111111111111111111111111</code>

##### Database Administrators App

Voice:

<code>GET http://example.appspot.com/call?service\_key=22222222222222222222222222222222&greeting=Leave+a+message+to+page+the+database+administrator+on+call</code>

SMS:

<code>GET http://example.appspot.com/sms?service\_key=22222222222222222222222222222222</code>

#### Twilio Phone Numbers
* 555-555-0111 - Server Administrators Number
    * Voice: `Server Administrators App`
    * SMS: `Server Administrators App`
* 555-555-0112 - Database Administrators Number
    * Voice: `Database Administrators App`
    * SMS: `Database Administrators App`
