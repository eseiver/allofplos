import datetime
import os
import re
import subprocess

import lxml.etree as et
from lxml import objectify
import requests

from . import Article
from .. import get_corpus_dir
from ..transformations import (filename_to_doi, _get_base_page, LANDING_PAGE_SUFFIX,
                               URL_SUFFIX, plos_page_dict, doi_url)
from ..plos_regex import validate_doi
from ..elements import (parse_article_date, get_contrib_info,
                        Journal, License, match_contribs_to_dicts)


class RemoteArticle(Article):
    """The primary object of a PLOS article, initialized by a valid PLOS DOI.

    """
    def __init__(self, doi, directory=None):
        """Creation of an article object.

        Usage:
        For the first time, you can use
        `article = Article(doi)`
        and then it and some attributes will be stored in memory.
        For creating articles after the first one, you can use:
        `article.doi = doi`
        This preserves the generic attributes and erases the article-specific ones
        (See also reset_memoized_attrs())
        Use this to more rapidly iterate through different articles.
        :param doi: The Digital Object Identifier of the article
        :type doi: str
        :param directory: where the local article XML file is located, defaults to None
        :type directory: str, optional
        """
        self.directory = directory if directory else get_corpus_dir()
        Article.__init__(self, doi=doi, directory=self.directory)

    def __str__(self, exclude_refs=True):
        """Output when you print an article object on the command line.

        For parsing and viewing the XML of a local article. Should not be used for hashing
        Excludes <back> element (including references list) for easier viewing
        :param exclude_refs: remove references from the article tree (eases print viewing)
        """
        parser = et.XMLParser(remove_blank_text=True)
        tree = et.parse(self.filename, parser)
        if exclude_refs:
            root = tree.getroot()
            back = tree.xpath('./back')
            root.remove(back[0])
        local_xml = et.tostring(tree,
                                method='xml',
                                encoding='unicode',
                                pretty_print=True)
        return local_xml

    def __repr__(self):
        """Value of an article object when you call it directly on the command line.

        Shows the DOI and title of the article
        :returns: DOI and title
        :rtype: {str}
        """
        return "Article container DOI: {0}".format(self.doi)

    def get_remote_xml(self):
        """For an article, parse its XML file at the location of self.url.

        Uses the lxml element tree to create the string, which is saved to a local
        file when downloaded
        :returns: string of entire remote article file
        :rtype: {str}
        """
        remote_xml = et.tostring(self.remote_tree,
                                 method='xml',
                                 encoding='unicode')
        return remote_xml

    def open_in_browser(self):
        """Opens the landing page (HTML) of an article in default browser.

        This is also the URL that the DOI resolves to
        """
        subprocess.call(["open", self.page])

    def check_if_link_works(self):
        """See if a link is valid (i.e., returns a '200' to the HTML request).

        Used for checking a URL to a PLOS article's landing page or XML file on journals.plos.org
        Full list of potential status codes: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        :return: boolean if HTTP status code returned available or unavailable,
        "error" if a different status code is returned than 200 or 404
        """
        request = requests.get(self.url)
        if request.status_code == 200:
            return True
        elif request.status_code == 404:
            return False
        else:
            return 'error'

    def check_if_doi_resolves(self, plos_valid=True):
        """Whether a PLOS DOI resolves via dx.doi.org to the correct article landing page.

        If the link works, make sure that it points to the same DOI
        Checks first if it's a valid DOI or see if it's a redirect.
        :return: 'works' if works as expected, 'doesn't work' if it doesn't resolve correctly,
        or if the metadata DOI doesn't match self.doi, return the metadata DOI
        """
        if plos_valid and validate_doi(self.doi) is False:
            return "Not valid PLOS DOI structure"
        url = "http://dx.doi.org/" + self.doi
        if self.check_if_link_works() is True:
            headers = {"accept": "application/vnd.citationstyles.csl+json"}
            r = requests.get(url, headers=headers)
            r_doi = r.json()['DOI']
            if r_doi == self.doi:
                return "works"
            else:
                return r_doi
        else:
            return "doesn't work"

    @property
    def remote_proof(self):
        """
        For a single article online, check whether it is an 'uncorrected proof' or a
        'VOR update' to the uncorrected proof, or neither.
        :return: proof status if it exists; otherwise, None
        """
        xpath_results = self.get_element_xpath(remote=True)
        proof = ''
        for result in xpath_results:
            if result.text == 'uncorrected-proof':
                proof = 'uncorrected_proof'
            elif result.text == 'vor-update-to-uncorrected-proof':
                proof = 'vor_update'
        return proof

    @property
    def remote_tree(self):
        """Gets the lxml element tree of an article from its remote URL.

        Can compare local (self.xml) to remote versions of XML
        :returns: article's online element tree
        :rtype: {lxml.etree._ElementTree-class}
        """
        return et.parse(self.url)