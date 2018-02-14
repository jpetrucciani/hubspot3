# coding: utf-8
import unittest
import uuid

import json
from nose.plugins.attrib import (
    attr
)
from . import (
    helper
)
from hubspot3.keywords import (
    KeywordsClient
)


class KeywordsClientTest(unittest.TestCase):
    """ Unit tests for the HubSpot Keyword API Python client.

    This file contains some unittest tests for the Keyword API.

    Questions, comments: http://docs.hubapi.com/wiki/Discussion_Group
    """
    def setUp(self):
        self.client = KeywordsClient(**helper.get_options())
        self.keyword_guids = None

    def tearDown(self):
        if (self.keyword_guids):
            list(map(
                lambda keyword_guid: self.client.delete_keyword(keyword_guid),
                self.keyword_guids
            ))

    @attr('api')
    def test_get_keywords(self):
        keywords = self.client.get_keywords()
        self.assertTrue(len(keywords))
        print(('\n\nGot some keywords: {}'.format(json.dumps(keywords))))

    @attr('api')
    def test_get_keyword(self):
        keywords = self.client.get_keywords()
        if len(keywords) < 1:
            self.fail('No keywords available for test.')

        keyword = keywords[0]
        print(('\n\nGoing to get a specific keyword: {}'.format(keyword)))

        result = self.client.get_keyword(keyword['keyword_guid'])
        self.assertEqual(keyword, result)

        print(('\n\nGot a single matching keyword: {}'.format(keyword['keyword_guid'])))

    @attr('api')
    def test_add_keyword(self):
        keyword = []
        # Add a single keyword to this self, it is a string with a uuid added because a string with
        # a random number appended to it has too high of a collision rate
        keyword.append('hubspot3_test_keyword{}'.format(str(uuid.uuid4())))

        # copy the keyword into 'result' after the client adds it
        result = self.client.add_keyword(keyword)

        # make sure 'result' has one keyword in it
        self.assertEqual(len(result['keywords']), 1)

        print('\n\nAdded keyword: {}'.format(json.dumps(result)))

        # holds the guid of the keyword being added
        self.keyword_guid = []

        # get the keyword's guid
        self.keyword_guid.append(result['keywords'][0]['keyword_guid'])

        # now check if the keyword is in the client

        # get what is in the client
        check = self.client.get_keywords()

        # filter 'check' if it is in this self
        check = [p for p in check if p['keyword_guid'] in self.keyword_guid]

        # check if it was filtered. If it was, it is in the client
        self.assertEqual(len(check), 1)

        print('\n\nSaved keyword {}'.format(json.dumps(check)))

    @attr('api')
    def test_add_keywords(self):
        # Add multiple Keywords in one API call.
        keywords = []
        for i in range(10):
            # A string with a random number between 0 and 1000 as a test keyword has too high
            # of a collision rate.
            # switched test string to a uuid to decrease collision chance.
            keywords.append('hubspot3_test_keyword{}'.format(str(uuid.uuid4())))

        # copy the keywords into 'result' after the client adds them
        result = self.client.add_keywords(keywords)

        # Now check if all of the keywords have been put in 'results'
        self.assertEqual(len(result), 10)

        # make and fill a list of 'keyword's guid's
        self.keyword_guids = []
        for keyword in result:
            self.keyword_guids.append(keyword['keyword_guid'])

        # This next section removes keywords from 'keywords' that are already in self by
        # checking the guid's. If none of the keywords in 'keywords' are already
        # there, it is done. Otherwise, fails at the assert.

        # Make sure they're in the list now
        keywords = self.client.get_keywords()

        keywords = [x for x in keywords if x['keyword_guid'] in self.keyword_guids]
        self.assertEqual(len(keywords), 10)

        print('\n\nAdded multiple keywords: {}'.format(keywords))

    @attr('api')
    def test_delete_keyword(self):
        # Delete multiple keywords in one API call.
        keyword = 'hubspot3_test_keyword{}'.format(str(uuid.uuid4()))
        result = self.client.add_keyword(keyword)
        keywords = result['keywords']
        first_keyword = keywords[0]
        print('\n\nAbout to delete a keyword, result= {}'.format(json.dumps(result)))

        self.client.delete_keyword(first_keyword['keyword_guid'])

        # Make sure it's not in the list now
        keywords = self.client.get_keywords()

        keywords = [x for x in keywords if x['keyword_guid'] == first_keyword['keyword_guid']]
        self.assertTrue(len(keywords) == 0)

        print('\n\nDeleted keyword {}'.format(json.dumps(first_keyword)))

    @attr('api')
    def test_utf8_keywords(self):
        # Start with base utf8 characters
        # TODO: Fails when adding simplified chinese char: 广 or cyrillic: л
        utf8_keyword_bases = ['é', 'ü']

        keyword_guids = []
        for utf8_keyword_base in utf8_keyword_bases:
            original_keyword = '{} - {}'.format(utf8_keyword_base, str(uuid.uuid4()))
            result = self.client.add_keyword(original_keyword)
            print('\n\nAdded keyword: {}'.format(json.dumps(result)))
            print(result)

            keywords_results = result.get('keywords')
            keyword_result = keywords_results[0]

            self.assertTrue(keyword_result['keyword_guid'])
            keyword_guids.append(keyword_result['keyword_guid'])

            actual_keyword = keyword_result['keyword']

            # Convert to utf-8 to compare strings. Returned string is \x-escaped
            if isinstance(original_keyword, str):
                original_unicode_keyword = original_keyword
            else:
                original_unicode_keyword = original_keyword.decode('utf-8')

            if isinstance(actual_keyword, str):
                actual_unicode_keyword = actual_keyword
            else:
                actual_unicode_keyword = actual_keyword.decode('utf-8')

            self.assertEqual(actual_unicode_keyword, original_unicode_keyword)


if __name__ == '__main__':
    unittest.main()
