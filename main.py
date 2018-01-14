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
import os

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import template

class UsersList(ndb.Model):
    user_ids = ndb.StringProperty(repeated=True)

class UserToHyperlink:
    def __init__(self, user_id, user_fullname):
        self.user_id = user_id
        self.user_fullname = user_fullname

class Profile(ndb.Model):
    # models a profile with necessary information
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    dob = ndb.DateProperty()
    phone = ndb.StringProperty()
    email = ndb.StringProperty()
    about_me = ndb.StringProperty()
    children = ndb.KeyProperty(repeated=True)
    schedule = ndb.KeyProperty(repeated=True) # list of Events
    # skills = ndb.StringProperty(repeated=True)

class Child(ndb.Model):
    # models a child with DOB
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    dob = ndb.DateProperty()

class Event(ndb.Model):
    # models a schedule with events that have a date, start time, end time,
    # and description
    date = ndb.DateProperty()
    start = ndb.IntegerProperty()
    end = ndb.IntegerProperty()
    description = ndb.StringProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        users_key = ndb.Key('UsersList', 'allUsers')
        all_users = users_key.get()
        if all_users is None:
            all_users = UsersList()
            all_users.key = ndb.Key('UsersList', 'allUsers')
            all_users.user_ids = []
            all_users.put()

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
        users_list = ndb.Key('UsersList', 'allUsers').get()
        if profile is None:
            profile = Profile()
            profile.key = ndb.Key('Profile', user.user_id())
            profile.schedule = []
            profile.put()
            users_list.user_ids.append(user.user_id())
            users_list.put()
            self.redirect('/editprofile')
        else:
            template_values = {
                'profile' : profile
            }
            path = os.path.join(os.path.dirname(__file__), 'MyProfile.html')
            self.response.out.write(template.render(path, template_values))
            

class EditProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        profile_key = ndb.Key('Profile', user.user_id())
        profile = profile_key.get()

        template_values = {
            'profile': profile
        }

        if profile is not None:
            path = os.path.join(os.path.dirname(__file__), 'editProfile.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')

class EditHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        profile_key = ndb.Key('Profile', user.user_id())
        profile = profile_key.get()

        profile.first_name = self.request.get('first_name')
        profile.last_name = self.request.get('last_name')
        profile.email = self.request.get('email')
        profile.phone = self.request.get('phone')
        profile.about_me = self.request.get('about_me')

        profile.put()

        self.redirect('/myprofile')

class ExploreHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        all_users = ndb.Key('UsersList', 'allUsers').get()
        UserToHyperlink_list = []
        for user_id in all_users.user_ids:
            if user_id != user.user_id():
                profile = ndb.Key('Profile', user_id).get()
                UserToHyperlink_list.append(UserToHyperlink(user_id, profile.first_name + ' ' + profile.last_name))

        template_values = {
            'users' : UserToHyperlink_list,
        }

        path = os.path.join(os.path.dirname(__file__), 'explore.html')
        self.response.out.write(template.render(path, template_values))

class DisplayProfile(webapp2.RequestHandler):
    def get(self):
        url_id = self.request.get('id')
        profile_key = ndb.Key('Profile', url_id)
        profile = profile_key.get()

        template_values = {
            'profile' : profile
        }

        path = os.path.join(os.path.dirname(__file__), 'DisplayProfile.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/myprofile', MyProfileHandler),
    ('/editprofile', EditProfileHandler),
    ('/edit', EditHandler),
    ('/explore', ExploreHandler),
    ('/viewprofile', DisplayProfile)
], debug=True)
