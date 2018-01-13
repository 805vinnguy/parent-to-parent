#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import urllib
import webapp2
import datetime

from google.appengine.ext import ndb
from google.appengine.api import users

class Profile(ndb.Model):
    # models a profile with necessary information
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    dob = ndb.DateProperty()
    phone = ndb.StringProperty()
    email = ndb.StringProperty()
    about_me = ndb.StringProperty()
    # children = ndb.KeyProperty(repeated=True)
    # skills = ndb.StringProperty(repeated=True)

class Child(ndb.Model):
    # models a child with DOB
    dob = ndb.DateProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('Hello, ' + user.nickname())
        else:
            self.response.write('Welcome! Please log in to get started.')

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url('/myprofile'))
        else:
            self.redirect('/myprofile')

class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect(users.create_logout_url('/'))
        else:
            self.redirect('/')

class MyProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        profile_key = ndb.Key('Profile', user.user_id())
        profile = profile_key.get()
        if profile is None:
            profile = Profile()
            profile.key = ndb.Key('Profile', user.user_id())
            profile.put()
            self.redirect('/editprofile')
        else:
            self.response.write(profile.first_name + ' ' + profile.last_name)

class EditProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        profile_key = ndb.Key('Profile', user.user_id())
        profile = profile_key.get()

        if profile is not None:
            self.response.out.write("""
                <html>
                    <body>
                        <form action="/edit" method="post">
                            First name:<br>
                            <input type="text" name="first_name"><br>
                            Last name:<br>
                            <input type="text" name="last_name"><br>
                            Email:<br>
                            <input type="text" name="email"><br>
                            Phone:<br>
                            <input type="text" name="phone"><br><br>
                            <input type="submit" value="Submit">
                        </form>
                    </body>
                </html>"""
            )
        else:
            self.redirect('/')

class EditHandler(webapp2.RequestHandler)
    def post(self):
        user = users.get_current_user()
        profile_key = ndb.Key('Profile', user.user_id())
        profile = profile_key.get()

        profile.first_name = self.request.get('first_name')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/myprofile', MyProfileHandler),
    ('/editprofile', EditProfileHandler),
    ('/edit', EditHandler)
], debug=True)
