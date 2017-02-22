import traceback
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse

from django.test import TestCase, RequestFactory, Client
from django.utils import timezone
from django.utils.timezone import localtime, now
from django.contrib.auth.models import User

from nadine.models.membership import *
from nadine.models.resource import Resource

today = localtime(now()).date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
one_month_from_now = today + relativedelta(months=1)
one_month_ago = today - relativedelta(months=1)

class MembershipTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='member_one', first_name='Member', last_name='One')

        # Not sure what this is --JLS
        # self.admin = User.objects.create_superuser(username='admin', email="blah@blah.com", password="secret")
        #self.client = Client()
        # success = self.client.login(username=self.admin.username, password="secret")

        # Resources
        self.test_resource = Resource.objects.create(name="Test Resource")

        # Membership package
        self.test_package = MembershipPackage.objects.create(name="Test Package")
        self.default_subscription = SubscriptionDefault.objects.create(
            package = self.test_package,
            resource = self.test_resource,
            allowance = 10,
            monthly_rate = 100,
            overage_rate = 20,
        )

        # Starts today and no end
        self.membership1 = self.create_membership(
            start = today,
            monthly_rate = 100,
        )

        # Starts today and ends in a month
        self.membership2 = self.create_membership(
            start = today,
            end = one_month_from_now,
            monthly_rate = 200.00,
        )

        # Starts in a month
        self.membership3 = self.create_membership(
            start = one_month_from_now,
            monthly_rate = 300.00,
        )

        # Started a month ago and ends today
        self.membership4 = self.create_membership(
            start = one_month_ago,
            end = today,
            monthly_rate = 400.00,
        )

        # Ended yesterday
        self.membership5 = self.create_membership(
            start = one_month_ago,
            end = yesterday,
            monthly_rate = 500.00,
        )

        # All last year
        self.membership6 = self.create_membership(
            start = date(year=today.year-1, month=1, day=1),
            end = date(year=today.year-1, month=12, day=31),
            monthly_rate = 600.00,
        )

        # Start and end on the same day of the month, last year for 8 months
        self.membership7 = self.create_membership(
            start = date(year=today.year-1, month=2, day=1),
            end =  date(year=today.year-1, month=10, day=1),
            monthly_rate = 700.00,
        )

        # Pro rated end
        self.membership8 = self.create_membership(
            start = date(year=today.year-1, month=2, day=1),
            end =  date(year=today.year-1, month=10, day=18),
            monthly_rate = 800.00,
        )

        # One period in the past
        self.membership9 = self.create_membership(
            start = date(year=today.year-1, month=2, day=1),
            end =  date(year=today.year-1, month=3, day=1),
            monthly_rate = 900.00,
        )

        # One period in the future
        self.membership10 = self.create_membership(
            start = date(year=today.year+1, month=3, day=1),
            end =  date(year=today.year+1, month=3, day=31),
            monthly_rate = 1000.00,
        )


    ############################################################################
    # Helper Methods
    ############################################################################


    def create_membership(self, bill_day=0, start=None, end=None, resource=None, monthly_rate=100, overage_rate=20):
        if not start:
            start = today
        if bill_day == 0:
            bill_day = start.day
        if not resource:
            resource = self.test_resource
        membership = Membership.objects.create(bill_day=bill_day)
        ResourceSubscription.objects.create(
            membership = membership,
            resource = resource,
            start_date = start,
            end_date = end,
            monthly_rate = monthly_rate,
            overage_rate = overage_rate,
        )
        return membership


    def period_boundary_test(self, period_start, period_end):
        # For a given period start, test the period_end is equal to the given period_end
        m = self.create_membership(start=period_start)
        ps, pe = m.get_period(target_date=period_start)
        # print("start: %s, end: %s, got: %s" % (period_start, period_end, pe))
        self.assertEquals(pe, period_end)


    def next_period_start_test(self, start, number):
        last_start = start
        m = self.create_membership(start=start)
        # print("Created Membership: start_date = %s, bill_day = %s" % (start, m.bill_day))
        for i in range(0, number):
            test_date = start + relativedelta(months=i) + timedelta(days=1)
            # print("  Test(%d): %s" % (i, test_date))
            this_start, this_end = m.get_period(test_date)
            next_start = m.next_period_start(last_start)
            # print("   This period: %s to %s, Next: %s" % (this_start, this_end, next_start))
            self.assertEqual(next_start, this_end + timedelta(days=1))
            self.assertEqual(last_start, this_start)
            last_start = next_start


    ############################################################################
    # Tests
    ############################################################################


    def test_inactive_period(self):
        # Today is outside the date range for this membership
        self.assertEquals((None, None), self.membership3.get_period(target_date=today))

    def test_get_period(self):
        # Test month bounderies
        self.period_boundary_test(date(2015, 1, 1), date(2015, 1, 31))
        self.period_boundary_test(date(2015, 2, 1), date(2015, 2, 28))
        self.period_boundary_test(date(2015, 3, 1), date(2015, 3, 31))
        self.period_boundary_test(date(2015, 4, 1), date(2015, 4, 30))
        self.period_boundary_test(date(2015, 5, 1), date(2015, 5, 31))
        self.period_boundary_test(date(2015, 6, 1), date(2015, 6, 30))
        self.period_boundary_test(date(2015, 7, 1), date(2015, 7, 31))
        self.period_boundary_test(date(2015, 8, 1), date(2015, 8, 31))
        self.period_boundary_test(date(2015, 9, 1), date(2015, 9, 30))
        self.period_boundary_test(date(2015, 10, 1), date(2015, 10, 31))
        self.period_boundary_test(date(2015, 11, 1), date(2015, 11, 30))
        self.period_boundary_test(date(2015, 12, 1), date(2015, 12, 31))

    def test_get_period_leap(self):
        # Leap year!
        self.period_boundary_test(date(2016, 2, 1), date(2016, 2, 29))
        self.period_boundary_test(date(2016, 3, 1), date(2016, 3, 31))

    def test_get_period_days(self):
        # Test Day bounderies
        for i in range(2, 31):
            self.period_boundary_test(date(2015, 7, i), date(2015, 8, i-1))

    def test_get_period_31st(self):
        # Test when the next following month has fewer days
        self.period_boundary_test(date(2015, 1, 29), date(2015, 2, 28))
        self.period_boundary_test(date(2015, 1, 30), date(2015, 2, 28))
        self.period_boundary_test(date(2015, 1, 31), date(2015, 2, 28))
        self.period_boundary_test(date(2016, 3, 31), date(2016, 4, 30))
        self.period_boundary_test(date(2017, 5, 31), date(2017, 6, 30))

    def test_get_period_bug(self):
        # Found this bug when I was testing so I created a special test for it --JLS
        m = self.create_membership(start=date(2017, 1, 28))
        ps, pe = m.get_period(date(2017, 3, 1))
        self.assertEqual(ps, date(2017, 2, 28))
        self.assertEqual(pe, date(2017, 3, 27))

    def test_get_period_bug2(self):
        # Another bug I found when testing --JLS
        # Membership = 1/31/17, Bill Day = 31st
        m = self.create_membership(start=date(2017, 1, 31))
        #  First Period: 1/31/17 - 2/28/17
        #  Next Period: 3/1/17 - 3/30/17
        ps, pe = m.get_period(date(2017, 3, 2))
        self.assertEqual(ps, date(2017, 3, 1))
        self.assertEqual(pe, date(2017, 3, 30))
        #  Period: 3/31/17 - 4/30/17
        ps, pe = m.get_period(date(2017, 4, 2))
        self.assertEqual(ps, date(2017, 3, 31))
        self.assertEqual(pe, date(2017, 4, 30))
        #  Period: 5/1/17 - 5/30/17
        ps, pe = m.get_period(date(2017, 5, 2))
        self.assertEqual(ps, date(2017, 5, 1))
        self.assertEqual(pe, date(2017, 5, 30))
        #  Period: 5/31/17 - 6/30/17
        ps, pe = m.get_period(date(2017, 6, 2))
        self.assertEqual(ps, date(2017, 5, 31))
        self.assertEqual(pe, date(2017, 6, 30))
        #  Period: 7/1/17 - 7/30/17
        ps, pe = m.get_period(date(2017, 7, 2))
        self.assertEqual(ps, date(2017, 7, 1))
        self.assertEqual(pe, date(2017, 7, 30))
        #  Period: 7/31/17 - 8/30/17
        ps, pe = m.get_period(date(2017, 8, 2))
        self.assertEqual(ps, date(2017, 7, 31))
        self.assertEqual(pe, date(2017, 8, 30))

    def test_is_period_boundary(self):
        m = self.create_membership(start=date(2016,1,1), end=date(2016,5,31))
        self.assertFalse(m.is_period_boundary(target_date=date(2016, 2, 15)))
        self.assertTrue(m.is_period_boundary(target_date=date(2016, 2, 29)))
        self.assertFalse(m.is_period_boundary(target_date=date(2016, 3, 15)))
        self.assertTrue(m.is_period_boundary(target_date=date(2016, 3, 31)))
        self.assertFalse(m.is_period_boundary(target_date=date(2016, 4, 15)))
        self.assertTrue(m.is_period_boundary(target_date=date(2016, 4, 30)))

    def test_next_period_start_active(self):
        self.assertEqual(self.membership1.next_period_start(), one_month_from_now)
        self.assertEqual(self.membership2.next_period_start(), one_month_from_now)

    def test_next_period_start_inactive(self):
        self.assertEqual(self.membership4.next_period_start(), None)
        self.assertEqual(self.membership5.next_period_start(), None)
        self.assertEqual(self.membership6.next_period_start(), None)
        self.assertEqual(self.membership7.next_period_start(), None)
        self.assertEqual(self.membership8.next_period_start(), None)
        self.assertEqual(self.membership9.next_period_start(), None)

    def test_next_period_start_future(self):
        self.assertEqual(self.membership3.next_period_start(), one_month_from_now)
        next_start = self.membership10.next_period_start()
        self.assertEqual(next_start.month, 3)
        self.assertEqual(next_start.day, 1)

    def test_next_period_start(self):
        # Start a membership on each day of the month and make sure the next
        # five years have valid period ranges and the right next_period_start
        # for i in range(1, 31):
            # self.next_period_start_test(date(2016, 1, i), 60)
        self.next_period_start_test(date(2016,1,1), 60)
        self.next_period_start_test(date(2016,1,10), 60)
        self.next_period_start_test(date(2017,1,28), 60)
        self.next_period_start_test(date(2016,1,31), 60)

    def test_active_memberships(self):
        active_memberships = Membership.objects.active_memberships()
        self.assertTrue(self.membership1 in active_memberships)
        self.assertTrue(self.membership2 in active_memberships)
        self.assertFalse(self.membership3 in active_memberships)
        self.assertTrue(self.membership4 in active_memberships)
        self.assertFalse(self.membership5 in active_memberships)
        self.assertFalse(self.membership6 in active_memberships)

    def test_is_active(self):
        self.assertTrue(self.membership1.is_active())
        self.assertTrue(self.membership2.is_active())
        self.assertFalse(self.membership3.is_active())
        self.assertTrue(self.membership4.is_active())
        self.assertFalse(self.membership5.is_active())
        self.assertFalse(self.membership6.is_active())
        self.assertFalse(self.membership7.is_active())

    def test_in_future(self):
        self.assertFalse(self.membership1.in_future())
        self.assertFalse(self.membership2.in_future())
        self.assertTrue(self.membership3.in_future())
        self.assertFalse(self.membership4.in_future())
        self.assertFalse(self.membership5.in_future())
        self.assertFalse(self.membership6.in_future())
        self.assertTrue(self.membership10.in_future())

    def test_prorated(self):
        r = self.membership8.subscriptions.first()
        # The first month was a full period so no prorate
        ps, pe = self.membership8.get_period(r.start_date)
        self.assertEqual(1, r.prorate_for_period(ps, pe))
        # The last month was partial so it was prorated
        ps, pe = self.membership8.get_period(r.end_date)
        self.assertTrue(1 > r.prorate_for_period(ps, pe))

    # TODO
    # def test_generate_bill(self):
    #     # Assume that if we generate a bill we will have a bill
    #     self.assertEquals(0, self.membership1.bills.count())
    #     self.membership1.generate_bill(target_date=today)
    #     self.assertEquals(1, self.membership1.bills.count())
    #
    #     bill = self.membership1.bills.first()
    #     self.assertEquals(self.membership1.monthly_rate, bill.amount())
    #
    #     ps, pe = self.membership1.get_period(target_date=today)
    #     self.assertEquals(ps, bill.period_start)
    #     self.assertEquals(pe, bill.period_end)
    #
    # def test_generate_all_bills(self):
    #     self.assertEquals(0, self.membership6.bills.count())
    #     self.membership6.generate_all_bills()
    #     self.assertEquals(12, self.membership6.bills.count())

    def test_package_monthly_rate(self):
        self.assertEqual(self.test_package.monthly_rate(), self.default_subscription.monthly_rate)

    def test_set_to_package(self):
        user = User.objects.create(username='test_user1', first_name='Test', last_name='User')
        membership = user.membership

        membership.end(yesterday)
        self.assertFalse(membership.matches_package())
        self.assertEqual(0, membership.monthly_rate())

        membership.set_to_package(self.test_package, today)
        self.assertEqual(membership.package, self.test_package)
        self.assertEqual(membership.monthly_rate(), self.test_package.monthly_rate())
        self.assertTrue(membership.matches_package())


# Copyright 2017 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
