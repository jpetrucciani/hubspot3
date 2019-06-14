"""Commandline entry for the Hubspot client."""

import fire

from hubspot3 import Hubspot3


def main():
    fire.Fire(Hubspot3)


if __name__ == '__main__':
    main()
