from __future__ import absolute_import

import six

from sentry.models import Group
from sentry.testutils import APITestCase
from sentry.testutils.helpers.datetime import iso_format, before_now


class GroupEventsOldestTest(APITestCase):
    def setUp(self):
        super(GroupEventsOldestTest, self).setUp()
        self.login_as(user=self.user)

        project = self.create_project()
        min_ago = iso_format(before_now(minutes=1))
        two_min_ago = iso_format(before_now(minutes=2))

        self.event1 = self.store_event(
            data={"environment": "staging", "fingerprint": ["group_1"], "timestamp": two_min_ago},
            project_id=project.id,
        )

        self.event2 = self.store_event(
            data={"environment": "production", "fingerprint": ["group_1"], "timestamp": min_ago},
            project_id=project.id,
        )

        self.group = Group.objects.first()

    def test_simple(self):
        url = u"/api/0/issues/{}/events/oldest/".format(self.group.id)
        response = self.client.get(url, format="json")

        assert response.status_code == 200
        assert response.data["id"] == six.text_type(self.event1.event_id)
