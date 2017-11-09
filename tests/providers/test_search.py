# coding=utf-8
"""Provider parser tests."""
from __future__ import unicode_literals

import os

import vcr


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def test_search_daily(providers, limit=3):

    # Given
    for provider in providers:

        # When
        html = os.path.join(__location__, provider.type, provider.name,
                            provider.name + '_daily.yaml')

        with vcr.use_cassette(html):
            actual = provider.klass.search(provider.data['daily']['search_strings'])

        for i, result in enumerate(actual):
            # Only compare up to the info hash if we have magnets
            if provider.data['daily']['results'][i]['link'].startswith('magnet'):
                result['link'] = result['link'][:60]

            if provider.data['daily']['results'][i]['pubdate']:
                    result['pubdate'] = result['pubdate'].replace(hour=0, minute=0, second=0,
                                                                  microsecond=0, tzinfo=None)

            assert result == provider.data['daily']['results'][i]

            if i + 1 == limit:
                break


def test_search_backlog(providers, limit=2):

        # Given
        for provider in providers:

            # When
            html = os.path.join(__location__, provider.type, provider.name,
                                provider.name + '_backlog.yaml')

            with vcr.use_cassette(html):
                actual = provider.klass.search(provider.data['backlog']['search_strings'])

            for i, result in enumerate(actual):
                # Only compare up to the info hash if we have magnets
                if provider.data['backlog']['results'][i]['link'].startswith('magnet'):
                    result['link'] = result['link'][:60]

                if provider.data['backlog']['results'][i]['pubdate']:
                    result['pubdate'] = result['pubdate'].replace(hour=0, minute=0, second=0,
                                                                  microsecond=0, tzinfo=None)

                assert result == provider.data['backlog']['results'][i]

                if i + 1 == limit:
                    break
