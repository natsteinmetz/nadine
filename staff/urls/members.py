from django.conf.urls import include, url

from staff.views import members

urlpatterns = [
     url(r'^members/$', members.members, name='members'),
     url(r'^members/(?P<group>[^/]+)/$', members.members, name='member_group'),
     url(r'^bcc/$', members.bcc_tool, name='bcc_tool'),
     url(r'^bcc/(?P<group>[^/]+)/$', members.bcc_tool, name='group_bcc'),
     url(r'^deposits/$', members.security_deposits, name='deposits'),
     url(r'^export/$', members.export_users, name='export_users'),
     url(r'^search/$', members.member_search, name='search'),
     url(r'^user_reports/$', members.view_user_reports, name='user_reports'),
     url(r'^slack_users/$', members.slack_users, name='slack_users'),
     url(r'^membership/(?P<username>[^/]+)/$', members.membership, name='membership'),
     url(r'^organizations/$', members.org_list, name='organizations'),
     url(r'^organization/(?P<org_id>\d+)$', members.org_view, name='organization'),

     url(r'^files/(?P<username>[^/]+)/$', members.files, name='files'),
     url(r'^detail/(?P<username>[^/]+)/$', members.detail, name='detail'),

     # TODO - remove
     url(r'^old/membership/(?P<membership_id>\d+)/$', members.old_membership, name='old_membership'),
     url(r'^old/add_membership/(?P<username>[^/]+)/$', members.old_add_membership, name='old_add_membership'),
     url(r'^old/memberships/(?P<username>[^/]+)/$', members.old_membership, name='old_memberships'),
]

# Copyright 2017 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.