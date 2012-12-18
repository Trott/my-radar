import webapp2
import jinja2
import os
import json
import re

from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Tag(db.Model):
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    accuracy = db.IntegerProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'tag_id': ''
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        if os.environ.get('HTTP_HOST'):
            hostname = os.environ['HTTP_HOST']
        else:
            hostname = os.environ['SERVER_NAME']

        scheme = os.environ.get('wsgi.url_scheme', 'http')

        template_values = {
            'tag_id': re.sub(r'\W+', '', self.request.get('tag_id')),
            'hostname': hostname,
            'scheme': scheme,
        }
        template = jinja_environment.get_template('track.html')
        self.response.out.write(template.render(template_values))


class Tracker(webapp2.RequestHandler):
    def get(self):
        tag_id = re.sub(r'\W+', '', self.request.get('tag'))
        if tag_id != "":
            position = Tag.get_by_key_name(tag_id)

            if position != None:
                template_values = {
                    'tag_id': tag_id,
                    'latitude': position.latitude,
                    'longitude': position.longitude,
                    'accuracy': position.accuracy
                }
            else:
                template_values = {
                    'error': "No tracking info for this tag."
                }
            template = jinja_environment.get_template('tracker.html')
            self.response.out.write(template.render(template_values))


class Update(webapp2.RequestHandler):
    def post(self):
        tag_id = re.sub(r'\W+', '', self.request.get('tag'))
        latitude = self.request.get('latitude')
        longitude = self.request.get('longitude')
        accuracy = self.request.get('accuracy')

        if tag_id != "" and latitude != "" and longitude != "" and accuracy != "":
            tag_id = str(tag_id)

            tag = Tag(key_name=tag_id)
            tag.latitude = float(json.loads(latitude))
            tag.longitude = float(json.loads(longitude))
            tag.accuracy = int(json.loads(accuracy))
            tag.put()


class GetLocation(webapp2.RequestHandler):
    def get(self):
        tag_id = self.request.get('tag')
        if tag_id != "":

            position = Tag.get_by_key_name(tag_id)

            if position != None:
                self.response.out.write(json.dumps({
                    'latitude': position.latitude,
                    'longitude': position.longitude}))


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/track', Tracker),
                               ('/update', Update),
                               ('/get', GetLocation)],
                              debug=False)
