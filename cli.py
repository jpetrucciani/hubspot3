"""Commandline entry for the Hubspot client."""

import inspect

import fire
from fire.completion import _IncludeMember
from hubspot3 import Hubspot3
from hubspot3.base import BaseClient


def filter_members(member) -> tuple:
    """Return only public API components."""
    name, component = member
    if isinstance(component, BaseClient) or inspect.ismethod(component):
        print(type(member))
        return member


def get_members(component, verbose: bool = False) -> list:
    """Retrieve all members of a component."""
    if isinstance(component, dict):
        members = component.items()
    else:
        members = inspect.getmembers(component)
    members = filter(filter_members, members)
    return [(member_name, member) for member_name, member in members if _IncludeMember(member_name, verbose)]


def main():
    fire.completion._Members = get_members
    fire.Fire(Hubspot3)


if __name__ == "__main__":
    main()
