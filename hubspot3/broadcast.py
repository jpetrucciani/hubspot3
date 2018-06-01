"""
hubspot broadcast api
"""
from hubspot3.base import BaseClient


HUBSPOT_BROADCAST_API_VERSION = "1"


class BaseSocialObject(object):
    """base social object"""

    def _camel_case_to_underscores(self, text):
        result = []
        pos = 0
        while pos < len(text):
            if text[pos].isupper():
                if (
                    pos - 1 > 0
                    and text[pos - 1].islower()
                    or pos - 1 > 0
                    and pos + 1 < len(text)
                    and text[pos + 1].islower()
                ):
                    result.append("_{}".format(text[pos].lower()))
                else:
                    result.append(text[pos].lower())
            else:
                result.append(text[pos])
            pos += 1
        return "".join(result)

    def _underscores_to_camel_case(self, text):
        result = []
        pos = 0
        while pos < len(text):
            if text[pos] == "_" and pos + 1 < len(text):
                result.append("{}".format(text[pos + 1].upper()))
                pos += 1
            else:
                result.append(text[pos])
            pos += 1
        return "".join(result)

    def to_dict(self):
        dict_self = {}
        for key in vars(self):
            dict_self[self._underscores_to_camel_case(key)] = getattr(self, key)
        return dict_self

    def from_dict(self, data):
        accepted_fields = self.accepted_fields()
        for key in data:
            if key in accepted_fields:
                setattr(self, self._camel_case_to_underscores(key), data[key])


class Broadcast(BaseSocialObject):
    """Defines a social media broadcast message for the broadcast api"""

    # Constants for remote content type
    COS_LP = "coslp"
    COS_BLOG = "cosblog"
    LEGACY_LP = "cmslp"
    LEGACY_BLOG = "cmsblog"

    def __init__(self, broadcast_data):
        self.data_parse(broadcast_data)

    def accepted_fields(self):
        return [
            "broadcastGuid",
            "campaignGuid",
            "channel",
            "channelGuid",
            "clicks",
            "clientTag",
            "content",
            "createdAt",
            "createdBy",
            "finishedAt",
            "groupGuid",
            "interactions",
            "interactionCounts",
            "linkGuid",
            "message",
            "messageUrl",
            "portalId",
            "remoteContentId",
            "remoteContentType",
            "status",
            "triggerAt",
            "updatedBy",
        ]

    def data_parse(self, broadcast_data):
        self.from_dict(broadcast_data)


class Channel(BaseSocialObject):
    """Defines the social media channel for the broadcast api"""

    def __init__(self, channel_data):
        self.data_parse(channel_data)

    def accepted_fields(self):
        return [
            "channelGuid",
            "accountGuid",
            "account",
            "type",
            "name",
            "dataMap",
            "createdAt",
            "settings",
        ]

    def data_parse(self, channel_data):
        self.from_dict(channel_data)


class BroadcastClient(BaseClient):
    """Broadcast API to manage messages published to social networks"""

    def _get_path(self, subpath):
        return "broadcast/v{}/{}".format(HUBSPOT_BROADCAST_API_VERSION, subpath)

    def get_broadcast(self, broadcast_guid, **kwargs):
        """
        Get a specific broadcast by guid
        """
        params = kwargs
        broadcast = self._call(
            "broadcasts/{}".format(broadcast_guid),
            params=params,
            content_type="application/json",
        )
        return Broadcast(broadcast)

    def get_broadcasts(
        self, broadcast_type="", page=None, remote_content_id=None, limit=None, **kwargs
    ):
        """
        Get all broadcasts, with optional paging and limits.
        Type filter can be 'scheduled', 'published' or 'failed'
        """
        if remote_content_id:
            return self.get_broadcasts_by_remote(remote_content_id)

        params = {"type": broadcast_type}
        if page:
            params["page"] = page

        params.update(kwargs)

        result = self._call(
            "broadcasts", params=params, content_type="application/json"
        )
        broadcasts = [Broadcast(b) for b in result]

        if limit:
            return broadcasts[:limit]
        return broadcasts

    def create_broadcast(self, broadcast):
        if not isinstance(broadcast, dict):
            return self._call(
                "broadcasts",
                data=broadcast.to_dict(),
                method="POST",
                content_type="application/json",
            )
        return self._call(
            "broadcasts", data=broadcast, method="POST", content_type="application/json"
        )

    def cancel_broadcast(self, broadcast_guid):
        """
        Cancel a broadcast specified by guid
        """
        subpath = "broadcasts/{}/update".format(broadcast_guid)
        broadcast = {"status": "CANCELED"}
        bcast_dict = self._call(
            subpath, method="POST", data=broadcast, content_type="application/json"
        )
        return bcast_dict

    def get_channel(self, channel_guid):
        channel = self._call(
            "channels/{}".format(channel_guid), content_type="application/json"
        )
        return Channel(channel)

    def get_channels(self, current=True, publish_only=False, settings=False):
        """
        if "current" is false it will return all channels that a user
        has published to in the past.

        if publish_only is set to true, then return only the channels
        that are publishable.

        if settings is true, the API will make extra queries to return
        the settings for each channel.
        """
        if publish_only:
            if current:
                endpoint = "channels/setting/publish/current"
            else:
                endpoint = "channels/setting/publish"
        else:
            if current:
                endpoint = "channels/current"
            else:
                endpoint = "channels"

        result = self._call(
            endpoint, content_type="application/json", params=dict(settings=settings)
        )
        return [Channel(c) for c in result]
