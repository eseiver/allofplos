import os

import requests

from . import Corpus
from .. import get_corpus_dir
from ..transformations import BASE_URL_API

corpus_dir = get_corpus_dir()
proofs_dir = os.path.join(corpus_dir, 'uncorrected_proofs')

class Proofs(Corpus):
    """Class of uncorrected proofs. Inherits from Corpus class."""
    def __init__(self, directory=None, extension='.xml', seed=None):
        if directory is None:
            directory = proofs_dir
        Corpus.__init__(self, directory=directory, extension=extension, seed=seed)
        self.directory = directory

    def check(self):
        """Make sure that every article in the corpus is an uncorrected proof."""
        for article in Proofs():
            assert article.proof == 'uncorrected_proof'
        print('True')

    def vor_updates(self):
        """
        For existing uncorrected proofs, check whether a vor is available to download
        :return: List of uncorrected proofs for which Solr says there is a VOR waiting
        """

        # First get/make list of uncorrected proofs
        uncorrected_list = list()

        # Create article list chunks for Solr query no longer than 10 DOIs at a time
        list_chunks = [self.dois[x:x+10] for x in range(0, len(self.dois), 10)]
        vor_updates_available = []
        for chunk in list_chunks:
            article_solr_string = ' OR '.join(chunk)

            # Get up to 10 article records from Solr
            # Filtered for publication_stage = vor-update-to-corrected-proof
            VOR_check_url_base = [BASE_URL_API,
                                  '?q=id:(',
                                  article_solr_string,
                                  ')&fq=publication_stage:vor-update-to-uncorrected-proof&',
                                  'fl=publication_stage,+id&wt=json&indent=true']
            VOR_check_url = ''.join(VOR_check_url_base)
            vor_check = requests.get(VOR_check_url).json()['response']['docs']
            vor_chunk_results = [x['id'] for x in vor_check]
            vor_updates_available.extend(vor_chunk_results)

        if vor_updates_available:
            print(len(vor_updates_available), "VOR updates indexed in Solr.")
        else:
            print("No VOR updates indexed in Solr.")
        return vor_updates_available

    def prune_proofs(self):
        """Remove articles in the proofs folder if they exist in the main directory."""


