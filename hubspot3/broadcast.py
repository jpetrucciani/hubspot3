"""
hubspot broadcast api
"""

from typing import Any, Dict, List, Optional
from hubspot3.base import BaseClient


HUBSPOT_BROADCAST_API_VERSION = "1"


class BaseSocialObject:
    """base social object"""

    def _camel_case_to_underscores(self, text: str) -> str:
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
                    result.append(f"_{text[pos].lower()}")
                else:
                    result.append(text[pos].lower())
            else:
                result.append(text[pos])
            pos += 1
        return "".join(result)

    def _underscores_to_camel_case(self, text: str) -> str:
        result = []
        pos = 0
        while pos < len(text):
            if text[pos] == "_" and pos + 1 < len(text):
                result.append(f"{text[pos + 1].upper()}")
                pos += 1
            else:
                result.append(text[pos])
            pos += 1
        return "".join(result)

    def to_dict(self) -> Dict:
        dict_self = {}
        for key in vars(self):
            dict_self[self._underscores_to_camel_case(key)] = getattr(self, key)
        return dict_self

    def accepted_fields(self) -> List[str]:
        return []

    def from_dict(self, data: Dict) -> None:
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

    def __init__(self, broadcast_data: Dict) -> None:
        self.data_parse(broadcast_data)

    def accepted_fields(self) -> List[str]:
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

    def data_parse(self, broadcast_data: Dict) -> None:
        self.from_dict(broadcast_data)


class Channel(BaseSocialObject):
    """Defines the social media channel for the broadcast api"""

    def __init__(self, channel_data: Dict) -> None:
        self.data_parse(channel_data)

    def accepted_fields(self) -> List[str]:
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

    def data_parse(self, channel_data: Dict) -> None:
        self.from_dict(channel_data)


class BroadcastClient(BaseClient):
    """Broadcast API to manage messages published to social networks"""

    def _get_path(self, subpath: str) -> str:
        return f"broadcast/v{HUBSPOT_BROADCAST_API_VERSION}/{subpath}"

    def get_broadcast(self, broadcast_guid: str, **kwargs: Any) -> Broadcast:
        """
        Get a specific broadcast by guid
        """
        params = kwargs
        broadcast = self._call(
            f"broadcasts/{broadcast_guid}",
            params=params,
            content_type="application/json",
        )
        return Broadcast(broadcast)

    def get_broadcasts(
        self,
        broadcast_type: str = "",
        page: str = "",
        remote_content_id: str = "",
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Broadcast]:
        """
        Get all broadcasts, with optional paging and limits.
        Type filter can be 'scheduled', 'published' or 'failed'
        """
        if remote_content_id:
            return self.get_broadcasts_by_remote(remote_content_id)  # type: ignore

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

    def create_broadcast(self, broadcast: Dict) -> Dict:
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

    def cancel_broadcast(self, broadcast_guid: str) -> Dict:
        """
        Cancel a broadcast specified by guid
        """
        subpath = f"broadcasts/{broadcast_guid}/update"
        broadcast = {"status": "CANCELED"}
        bcast_dict = self._call(
            subpath, method="POST", data=broadcast, content_type="application/json"
        )
        return bcast_dict

    def get_channel(self, channel_guid: str) -> Channel:
        channel = self._call(
            f"channels/{channel_guid}", content_type="application/json"
        )
        return Channel(channel)

    def get_channels(
        self, current: bool = True, publish_only: bool = False, settings: bool = False
    ) -> List[Channel]:
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
