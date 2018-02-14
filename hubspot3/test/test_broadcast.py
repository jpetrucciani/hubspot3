import time
import unittest
from nose.plugins.attrib import (
    attr
)
from hubspot3.test import (
    helper
)
from hubspot3.broadcast import (
    Broadcast,
    BroadcastClient
)


class BroadcastClientTest(unittest.TestCase):
    """ Unit tests for the HubSpot Broadcast API Python client.

    This file contains some unittest tests for the Broadcast API.

    Questions, comments: http://docs.hubapi.com/wiki/Discussion_Group
    """
    def setUp(self):
        self.client = BroadcastClient(**helper.get_options())
        self.broadcast_guids = None

    def tearDown(self):
        # Cancel any broadcasts created as part of the tests
        if self.broadcast_guids:
            list(map(self.client.cancel_broadcast, self.broadcast_guids))

    @attr('api')
    def test_get_broadcasts(self):
        # Should fetch at least 1 broadcast on the test portal 62515
        broadcasts = self.client.get_broadcasts(limit=1)
        self.assertTrue(len(broadcasts) > 0)

        broadcast = broadcasts[0].to_dict()
        self.assertIsNotNone(broadcast['channelGuid'])
        print('\n\nFetched some broadcasts')

        broadcast_guid = broadcast['broadcastGuid']
        # Re-fetch the broadcast using different call
        bcast = self.client.get_broadcast(broadcast_guid)
        # Should have expected fields
        self.assertIsNotNone(bcast.broadcast_guid)
        self.assertIsNotNone(bcast.channel_guid)
        self.assertIsNotNone(bcast.status)

    @attr('api')
    def test_get_channels(self):
        # Fetch older channels ensured to exist
        channels = self.client.get_channels(current=True)
        self.assertTrue(len(channels) > 0)

    @attr('api')
    def test_create_broadcast(self):
        content = dict(body='Test hubspot3 unit tests http://www.hubspot.com')
        channels = self.client.get_channels(current=True, publish_only=True)
        if len(channels) == 0:
            self.fail('Failed to find a publishable channel')

        channel = channels[0]

        # Get a trigger in the future
        trigger_at = int(time.time() + 6000) * 1000
        bcast = Broadcast({
            'content': content,
            'triggerAt': trigger_at,
            'channelGuid': channel.channel_guid
        })

        try:
            resp = self.client.create_broadcast(bcast)
            broadcast = Broadcast(resp)
            self.assertIsNotNone(broadcast.broadcast_guid)
            self.assertEqual(channel.channel_guid, broadcast.channel_guid)
            # Ensure it is canceled
            self.broadcast_guids = []
            self.broadcast_guids.append(broadcast.broadcast_guid)
        except Exception as e:
            self.fail('Should not have raised exception: {}'.format(e))


if __name__ == '__main__':
    unittest.main()
