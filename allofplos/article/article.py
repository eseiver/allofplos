import datetime
import os
import re
import subprocess

import lxml.etree as et
from lxml import objectify
import requests

from .. import get_corpus_dir
from ..transformations import (filename_to_doi, _get_base_page, LANDING_PAGE_SUFFIX,
                               URL_SUFFIX, plos_page_dict, doi_url)
from ..plos_regex import validate_doi
from ..elements import (parse_article_date, get_contrib_info,
                        Journal, License, match_contribs_to_dicts)


class Article():
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
        self.doi = doi
        self.directory = directory if directory else get_corpus_dir()
        self.reset_memoized_attrs()
        self._editor = None
    
    def __eq__(self, other):
        doi_eq = self.doi == other.doi
        dir_eq = self.directory == other.directory
        return doi_eq and dir_eq

    def reset_memoized_attrs(self):
        """Reset attributes to None when instantiating a new article object.

        For article attributes that are memoized and specific to that particular article
        (including the XML tree and whether the xml file is in the local directory),
        reset them when creating a new article object.
        """
        self._tree = None
        self._local = None
        self._contributors = None

    @property
    def doi(self):
        """The unique Digital Object Identifier for a PLOS article.

        See https://www.doi.org/
        :returns: DOI of the article object
        :rtype: {str}
        """
        return self._doi

    @doi.setter
    def doi(self, d):
        """
        Using regular expressions, make sure the doi is valid before
        instantiating the article object.
        """
        if validate_doi(d) is False:
            raise Exception("Invalid format for PLOS DOI: {}".format(d))
        self.reset_memoized_attrs()
        self._doi = d

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
        if self.local:
            out = "DOI: {0}\nTitle: {1}".format(self.doi, self.title)
        else:
            out = "Article container DOI: {0}".format(self.doi)
        return out

    def doi_link(self):
        """The link of the DOI, which redirects to the journal URL."""
        return doi_url + self.doi

    def open_in_browser(self):
        """Opens the landing page (HTML) of an article in default browser.

        This is also the URL that the DOI resolves to
        """
        subprocess.call(["open", self.page])

    def get_page(self, page_type='article'):
        """Get any of the PLOS URLs associated with a particular DOI.

        Based on `get_page_base()`, which customizes the beginning URL by journal.
        :param page_type: one of the keys in `plos_page_dict`, defaults to article
        """
        BASE_LANDING_PAGE = _get_base_page(self.journal)
        try:
            page = BASE_LANDING_PAGE + LANDING_PAGE_SUFFIX.format(plos_page_dict[page_type],
                                                                  self.doi)
            if page_type == 'assetXMLFile':
                page += URL_SUFFIX
        except KeyError:
            raise Exception('Invalid page_type; value must be one of the following: {}'.format(list(plos_page_dict.keys())))
        return page

    @property
    def page(self):
        """ The URL of the landing page for an article.

        Where to access an article's HTML version
        """
        return self.get_page()

    @property
    def url(self):
        """The direct url of an article's XML file.
        """
        return self.get_page(page_type='assetXMLFile')

    @property
    def filename(self):
        """The path on the local file system to a given article's XML file
        """
        if 'annotation' in self.doi:
            article_path = os.path.join(self.directory, 'plos.correction.' + self.doi.split('/')[-1] + '.xml')
        else:
            article_path = os.path.join(self.directory, self.doi.lstrip('10.1371/') + '.xml')
        return article_path

    @property
    def local(self):
        """Boolean of whether the article is stored locally or not.

        Stored as attribute after first access
        """
        if self._local is None:
            self._local = os.path.isfile(self.filename)
        else:
            pass
        return self._local

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

    @property
    def journal(self):
        """Journal that an article was published in.
        Can be PLOS Biology, Medicine, Neglected Tropical Diseases, Pathogens,
        Genetics, Computational Biology, ONE, or the now defunct Clinical Trials.
        Relies on a simple doi_to_journal transform when possible, and uses `Journal().parse_plos_journal()`
        for the "annotation" DOIs that don't have that journal information in the DOI.
        """
        if 'annotation' not in self.doi:
            journal = Journal.doi_to_journal(self.doi)
        else:
            journal_meta = self.root.xpath('/article/front/journal-meta')[0]
            journal = str(Journal(journal_meta))
        return journal

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

    @filename.setter
    def filename(self, value):
        """Sets an article object using a local filename.

        Converts a filename to DOI using an existing function.
        :param value: filename
        :type value: string
        """
        self.doi = filename_to_doi(value)

    @classmethod
    def from_filename(cls, filename):
        """Initiate an article object using a local XML file.

        Will set `self.directory` if the full file path is available. If not, it will
        default to `get_corpus_dir()` via `Article().__init__`. This method is most useful
        for instantiating an Article object when the file is not in the default corpus
        directory, or when changing directories.
        """
        if os.path.isfile(filename):
            directory = os.path.dirname(filename)
        else:
            directory = None
        return cls(filename_to_doi(filename), directory=directory)
