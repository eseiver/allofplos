import datetime
import os
import unittest

from . import TESTDIR, TESTDATADIR
from .. import Article, Corpus, get_corpus_dir, starterdir

from ..transformations import (doi_to_path, url_to_path, filename_to_doi, url_to_doi,
                               filename_to_url, doi_to_url)
from ..corpus import listdir_nohidden, check_for_uncorrected_proofs, get_uncorrected_proofs


suffix = '.xml'
example_url = 'http://journals.plos.org/plosbiology/article/file?id=10.1371/'\
              'journal.pbio.2001413&type=manuscript'
example_file = 'journal.pbio.2001413.xml'
example_doi = '10.1371/journal.pbio.2001413'
example_url2 = 'http://journals.plos.org/plosone/article/file?id=10.1371/'\
               'annotation/3155a3e9-5fbe-435c-a07a-e9a4846ec0b6&type=manuscript'
example_file2 = 'plos.correction.3155a3e9-5fbe-435c-a07a-e9a4846ec0b6.xml'
example_doi2 = '10.1371/annotation/3155a3e9-5fbe-435c-a07a-e9a4846ec0b6'
example_uncorrected_doi = '10.1371/journal.pbio.2002399'
example_vor_doi = '10.1371/journal.pbio.2002354'
class_doi = '10.1371/journal.pone.0185809'


class TestDOIMethods(unittest.TestCase):

    def test_doi_conversions(self):
        """
        TODO: What this tests are about!
        """
        assert os.path.join(get_corpus_dir(), example_file) == doi_to_path(example_doi)
        assert example_file2 == doi_to_path(example_doi2, '')
        assert example_url2 == doi_to_url(example_doi2)
        assert example_url == doi_to_url(example_doi)

    def test_file_conversions(self):
        """
        TODO: What this tests are about!
                """
        assert example_doi == filename_to_doi(example_file)
        assert example_doi2 == filename_to_doi(example_file2)
        assert example_url == filename_to_url(example_file)
        assert example_url2 == filename_to_url(example_file2)

    def test_url_conversions(self):
        """
        TODO: What this tests are about!
        """
        assert example_doi == url_to_doi(example_url)
        assert example_doi2 == url_to_doi(example_url2)
        assert example_file == url_to_path(example_url, '')
        assert example_file2 == url_to_path(example_url2, '')


class TestArticleClass(unittest.TestCase):

    def test_class_doi1(self):
        """Tests the methods and properties of the Article class
        Test article DOI: 10.1371/journal.pone.0185809
        TODO: there is a socket warning from requests module. See https://github.com/requests/requests/issues/3912
        XML file is in test directory
        """
        article = Article(class_doi, directory=TESTDATADIR)
        assert article.amendment is False
        assert article.get_aff_dict() == {'aff001': 'Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands', 'aff002': 'Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany', 'aff003': 'University of Sussex, School of Life Sciences, Falmer, Brighton BN1 9QG, United Kingdom', 'edit1': 'University of Saskatchewan, CANADA'}
        assert article.get_contributions_dict() == {}
        assert article.get_contributors_info() == [{'contrib_initials': 'CAH', 'given_names': 'Caspar A.', 'surname': 'Hallmann', 'group_name': None, 'ids': [{'id_type': 'orcid', 'id': 'http://orcid.org/0000-0002-4630-0522', 'authenticated': 'true'}], 'rid_dict': {'corresp': ['cor001'], 'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'corresponding', 'editor_type': None, 'email': ['c.hallmann@science.ru.nl'], 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Formal analysis', 'Investigation', 'Methodology', 'Software', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'MS', 'given_names': 'Martin', 'surname': 'Sorg', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Funding acquisition', 'Investigation', 'Methodology', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'EJ', 'given_names': 'Eelke', 'surname': 'Jongejans', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Funding acquisition', 'Investigation', 'Supervision', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'HS', 'given_names': 'Henk', 'surname': 'Siepel', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Investigation', 'Supervision', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'NH', 'given_names': 'Nick', 'surname': 'Hofland', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Formal analysis', 'Resources', 'Software', 'Validation']}, 'footnotes': []}, {'contrib_initials': 'HS', 'given_names': 'Heinz', 'surname': 'Schwan', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Funding acquisition', 'Investigation', 'Methodology', 'Project administration', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'WS', 'given_names': 'Werner', 'surname': 'Stenmans', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Funding acquisition', 'Methodology', 'Project administration', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'AM', 'given_names': 'Andreas', 'surname': 'Müller', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Project administration', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'HS', 'given_names': 'Hubert', 'surname': 'Sumser', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Investigation', 'Methodology', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'TH', 'given_names': 'Thomas', 'surname': 'Hörren', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Investigation', 'Methodology', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'DG', 'given_names': 'Dave', 'surname': 'Goulson', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff003']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['University of Sussex, School of Life Sciences, Falmer, Brighton BN1 9QG, United Kingdom'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Investigation', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'HK', 'given_names': 'Hans', 'surname': 'de Kroon', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Funding acquisition', 'Investigation', 'Methodology', 'Resources', 'Supervision', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'EGL', 'given_names': 'Eric Gordon', 'surname': 'Lamb', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['edit1']}, 'contrib_type': 'editor', 'author_type': None, 'editor_type': None, 'email': None, 'affiliations': ['University of Saskatchewan, CANADA'], 'author_roles': {None: ['Editor']}, 'footnotes': []}]
        assert article.get_corr_author_emails() == {'cor001': ['c.hallmann@science.ru.nl']}
        assert article.get_dates() == {'collection': datetime.datetime(2017, 1, 1, 0, 0), 'epub': datetime.datetime(2017, 10, 18, 0, 0), 'received': datetime.datetime(2017, 7, 28, 0, 0), 'accepted': datetime.datetime(2017, 9, 19, 0, 0), 'updated': ''}
        assert article.get_fn_dict() == {'coi001': 'The authors have declared that no competing interests exist.'}
        assert article.get_related_dois() == {}
        assert article.get_page(page_type='assetXMLFile') == "http://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0185809&type=manuscript"
        assert article.abstract[:100] == "Global declines in insects have sparked wide interest among scientists, politicians, and the general"
        assert article.authors == [{'contrib_initials': 'CAH', 'given_names': 'Caspar A.', 'surname': 'Hallmann', 'group_name': None, 'ids': [{'id_type': 'orcid', 'id': 'http://orcid.org/0000-0002-4630-0522', 'authenticated': 'true'}], 'rid_dict': {'corresp': ['cor001'], 'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'corresponding', 'editor_type': None, 'email': ['c.hallmann@science.ru.nl'], 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Formal analysis', 'Investigation', 'Methodology', 'Software', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'MS', 'given_names': 'Martin', 'surname': 'Sorg', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Funding acquisition', 'Investigation', 'Methodology', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'EJ', 'given_names': 'Eelke', 'surname': 'Jongejans', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Funding acquisition', 'Investigation', 'Supervision', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'HS', 'given_names': 'Henk', 'surname': 'Siepel', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Investigation', 'Supervision', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'NH', 'given_names': 'Nick', 'surname': 'Hofland', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Formal analysis', 'Resources', 'Software', 'Validation']}, 'footnotes': []}, {'contrib_initials': 'HS', 'given_names': 'Heinz', 'surname': 'Schwan', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Funding acquisition', 'Investigation', 'Methodology', 'Project administration', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'WS', 'given_names': 'Werner', 'surname': 'Stenmans', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Funding acquisition', 'Methodology', 'Project administration', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'AM', 'given_names': 'Andreas', 'surname': 'Müller', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Project administration', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'HS', 'given_names': 'Hubert', 'surname': 'Sumser', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Investigation', 'Methodology', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'TH', 'given_names': 'Thomas', 'surname': 'Hörren', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Entomological Society Krefeld e.V., Entomological Collections Krefeld, Marktstrasse 159, 47798 Krefeld, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Data curation', 'Investigation', 'Methodology', 'Resources', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'DG', 'given_names': 'Dave', 'surname': 'Goulson', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff003']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['University of Sussex, School of Life Sciences, Falmer, Brighton BN1 9QG, United Kingdom'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Investigation', 'Writing – review & editing']}, 'footnotes': []}, {'contrib_initials': 'HK', 'given_names': 'Hans', 'surname': 'de Kroon', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Funding acquisition', 'Investigation', 'Methodology', 'Resources', 'Supervision', 'Writing – review & editing']}, 'footnotes': []}]
        assert article.corr_author == [{'contrib_initials': 'CAH', 'given_names': 'Caspar A.', 'surname': 'Hallmann', 'group_name': None, 'ids': [{'id_type': 'orcid', 'id': 'http://orcid.org/0000-0002-4630-0522', 'authenticated': 'true'}], 'rid_dict': {'corresp': ['cor001'], 'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'corresponding', 'editor_type': None, 'email': ['c.hallmann@science.ru.nl'], 'affiliations': ['Radboud University, Institute for Water and Wetland Research, Animal Ecology and Physiology & Experimental Plant Ecology, PO Box 9100, 6500 GL Nijmegen, The Netherlands'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Formal analysis', 'Investigation', 'Methodology', 'Software', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review & editing']}, 'footnotes': []}]
        assert article.amendment is False
        assert article.counts == {'fig-count': '5', 'table-count': '4', 'page-count': '21'}
        assert article.doi == "10.1371/journal.pone.0185809"
        assert article.dtd == "JATS 1.1d3"
        assert article.editor == [{'contrib_initials': 'EGL', 'given_names': 'Eric Gordon', 'surname': 'Lamb', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['edit1']}, 'contrib_type': 'editor', 'author_type': None, 'editor_type': None, 'email': None, 'affiliations': ['University of Saskatchewan, CANADA'], 'author_roles': {None: ['Editor']}, 'footnotes': []}]
        article_relpath = os.path.relpath(article.filename, TESTDIR)
        assert article_relpath == "testdata/journal.pone.0185809.xml"
        assert article.journal == "PLOS ONE"
        assert article.local is True
        assert article.page == "http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0185809"
        assert article.plostype == "Research Article"
        assert article.proof == ''
        assert article.pubdate == datetime.datetime(2017, 10, 18, 0, 0)
        assert article.related_dois == []
        assert article.taxonomy == {'heading': [('Research Article',)], 'Discipline-v3': [('Biology and life sciences', 'Organisms', 'Eukaryota', 'Animals', 'Invertebrates', 'Arthropoda', 'Insects'), ('Earth sciences', 'Seasons'), ('Earth sciences', 'Geography', 'Human geography', 'Land use'), ('Social sciences', 'Human geography', 'Land use'), ('Biology and life sciences', 'Ecology', 'Ecological metrics', 'Biomass (ecology)'), ('Ecology and environmental sciences', 'Ecology', 'Ecological metrics', 'Biomass (ecology)'), ('Ecology and environmental sciences', 'Conservation science'), ('Biology and life sciences', 'Ecology', 'Plant ecology', 'Plant communities', 'Grasslands'), ('Ecology and environmental sciences', 'Ecology', 'Plant ecology', 'Plant communities', 'Grasslands'), ('Biology and life sciences', 'Plant science', 'Plant ecology', 'Plant communities', 'Grasslands'), ('Ecology and environmental sciences', 'Terrestrial environments', 'Grasslands'), ('Biology and life sciences', 'Ecology', 'Ecological metrics', 'Species diversity'), ('Ecology and environmental sciences', 'Ecology', 'Ecological metrics', 'Species diversity'), ('Biology and life sciences', 'Organisms', 'Eukaryota', 'Plants', 'Herbs')]}, "Taxonomy not retrieved as expected for {0}".format(article.doi)
        assert article.title == "More than 75 percent decline over 27 years in total flying insect biomass in protected areas"
        assert article.type_ == "research-article"
        assert article.url == "http://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0185809&type=manuscript"
        assert article.word_count == 6646
        assert article.license == {'license': 'CC-BY 4.0', 'license_link': 'https://creativecommons.org/licenses/by/4.0/', 'copyright_holder': 'Hallmann et al', 'copyright_year': 2017}

    def test_example_doi(self):
        """Tests the methods and properties of the Article class
        Test article DOI: 10.1371/journal.pbio.2001413
        XML file is in test directory
        """
        article = Article(example_doi, directory=TESTDATADIR)
        assert article.amendment is False
        assert article.get_aff_dict() == {'aff001': 'Department of Bioengineering, Stanford University, Stanford, California, United States of America', 'aff002': 'Isaac Newton Graham Middle School, Mountain View, California, United States of America', 'aff003': 'MYP Dresden International School, Dresden, Germany', 'aff004': 'University of California Santa Cruz, Santa Cruz, California, United States of America', 'aff005': 'Georgia Institute of Technology, Atlanta, Georgia, United States of America'}
        assert article.get_contributions_dict() == {}
        assert article.get_contributors_info() == [{'contrib_initials': 'LCG', 'given_names': 'Lukas C.', 'surname': 'Gerber', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Department of Bioengineering, Stanford University, Stanford, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Formal analysis', 'Investigation', 'Methodology', 'Resources', 'Software', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review and editing']}, 'footnotes': []}, {'contrib_initials': 'ACK', 'given_names': 'Agnes', 'surname': 'Calasanz-Kaiser', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Isaac Newton Graham Middle School, Mountain View, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Formal analysis', 'Investigation', 'Resources', 'Software', 'Supervision']}, 'footnotes': []}, {'contrib_initials': 'LH', 'given_names': 'Luke', 'surname': 'Hyman', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff003']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['MYP Dresden International School, Dresden, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Investigation', 'Software']}, 'footnotes': []}, {'contrib_initials': 'KV', 'given_names': 'Kateryna', 'surname': 'Voitiuk', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff004']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['University of California Santa Cruz, Santa Cruz, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Investigation', 'Software']}, 'footnotes': []}, {'contrib_initials': 'UP', 'given_names': 'Uday', 'surname': 'Patil', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff005']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Georgia Institute of Technology, Atlanta, Georgia, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Investigation', 'Software']}, 'footnotes': []}, {'contrib_initials': 'IHRK', 'given_names': 'Ingmar H.', 'surname': 'Riedel-Kruse', 'group_name': None, 'ids': [{'id_type': 'orcid', 'id': 'http://orcid.org/0000-0002-6068-5561', 'authenticated': 'true'}], 'rid_dict': {'aff': ['aff001'], 'corresp': ['cor001']}, 'contrib_type': 'author', 'author_type': 'corresponding', 'editor_type': None, 'email': ['ingmar@stanford.edu'], 'affiliations': ['Department of Bioengineering, Stanford University, Stanford, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Formal analysis', 'Funding acquisition', 'Investigation', 'Methodology', 'Project administration', 'Resources', 'Software', 'Supervision', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review and editing']}, 'footnotes': []}]
        assert article.get_corr_author_emails() == {'cor001': ['ingmar@stanford.edu']}
        assert article.get_dates() == {'epub': datetime.datetime(2017, 3, 21, 0, 0), 'collection': datetime.datetime(2017, 3, 1, 0, 0), 'updated': ''}
        assert article.get_fn_dict() == {'coi001': 'The authors have declared that no competing interests exist.'}
        assert article.get_related_dois() == {}
        assert article.get_page(page_type='assetXMLFile') == "http://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.2001413&type=manuscript"
        assert article.abstract[:100] == "Liquid-handling robots have many applications for biotechnology and the life sciences, with increasi"
        assert article.authors == [{'contrib_initials': 'LCG', 'given_names': 'Lukas C.', 'surname': 'Gerber', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff001']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Department of Bioengineering, Stanford University, Stanford, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Formal analysis', 'Investigation', 'Methodology', 'Resources', 'Software', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review and editing']}, 'footnotes': []}, {'contrib_initials': 'ACK', 'given_names': 'Agnes', 'surname': 'Calasanz-Kaiser', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff002']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Isaac Newton Graham Middle School, Mountain View, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Formal analysis', 'Investigation', 'Resources', 'Software', 'Supervision']}, 'footnotes': []}, {'contrib_initials': 'LH', 'given_names': 'Luke', 'surname': 'Hyman', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff003']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['MYP Dresden International School, Dresden, Germany'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Investigation', 'Software']}, 'footnotes': []}, {'contrib_initials': 'KV', 'given_names': 'Kateryna', 'surname': 'Voitiuk', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff004']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['University of California Santa Cruz, Santa Cruz, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Investigation', 'Software']}, 'footnotes': []}, {'contrib_initials': 'UP', 'given_names': 'Uday', 'surname': 'Patil', 'group_name': None, 'ids': [], 'rid_dict': {'aff': ['aff005']}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': ['Georgia Institute of Technology, Atlanta, Georgia, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Investigation', 'Software']}, 'footnotes': []}, {'contrib_initials': 'IHRK', 'given_names': 'Ingmar H.', 'surname': 'Riedel-Kruse', 'group_name': None, 'ids': [{'id_type': 'orcid', 'id': 'http://orcid.org/0000-0002-6068-5561', 'authenticated': 'true'}], 'rid_dict': {'aff': ['aff001'], 'corresp': ['cor001']}, 'contrib_type': 'author', 'author_type': 'corresponding', 'editor_type': None, 'email': ['ingmar@stanford.edu'], 'affiliations': ['Department of Bioengineering, Stanford University, Stanford, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Formal analysis', 'Funding acquisition', 'Investigation', 'Methodology', 'Project administration', 'Resources', 'Software', 'Supervision', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review and editing']}, 'footnotes': []}]
        assert article.corr_author == [{'contrib_initials': 'IHRK', 'given_names': 'Ingmar H.', 'surname': 'Riedel-Kruse', 'group_name': None, 'ids': [{'id_type': 'orcid', 'id': 'http://orcid.org/0000-0002-6068-5561', 'authenticated': 'true'}], 'rid_dict': {'aff': ['aff001'], 'corresp': ['cor001']}, 'contrib_type': 'author', 'author_type': 'corresponding', 'editor_type': None, 'email': ['ingmar@stanford.edu'], 'affiliations': ['Department of Bioengineering, Stanford University, Stanford, California, United States of America'], 'author_roles': {'CASRAI CREDiT taxonomy': ['Conceptualization', 'Data curation', 'Formal analysis', 'Funding acquisition', 'Investigation', 'Methodology', 'Project administration', 'Resources', 'Software', 'Supervision', 'Validation', 'Visualization', 'Writing – original draft', 'Writing – review and editing']}, 'footnotes': []}]
        assert article.amendment is False
        assert article.counts == {'fig-count': '3', 'table-count': '0', 'page-count': '9'}
        assert article.doi == "10.1371/journal.pbio.2001413"
        assert article.dtd == "JATS 1.1d3"
        assert article.editor == []
        article_relpath = os.path.relpath(article.filename, TESTDIR)
        assert article_relpath == "testdata/journal.pbio.2001413.xml"
        assert article.journal == "PLOS Biology"
        assert article.local is True
        assert article.page == "http://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.2001413"
        assert article.plostype == "Community Page"
        assert article.proof == ''
        assert article.pubdate == datetime.datetime(2017, 3, 21, 0, 0)
        assert article.related_dois == []
        assert article.taxonomy == {'Discipline-v3': [('Engineering and technology',
                                                       'Mechanical engineering',
                                                       'Robotics',
                                                       'Robots'),
                                                      ('Engineering and technology',
                                                       'Equipment',
                                                       'Laboratory equipment',
                                                       'Pipettes'),
                                                      ('Engineering and technology', 'Mechanical engineering', 'Robotics'),
                                                      ('Social sciences', 'Sociology', 'Education', 'Schools'),
                                                      ('Biology and life sciences',
                                                       'Neuroscience',
                                                       'Cognitive science',
                                                       'Cognitive psychology',
                                                       'Learning',
                                                       'Human learning'),
                                                      ('Biology and life sciences',
                                                       'Psychology',
                                                       'Cognitive psychology',
                                                       'Learning',
                                                       'Human learning'),
                                                      ('Social sciences',
                                                       'Psychology',
                                                       'Cognitive psychology',
                                                       'Learning',
                                                       'Human learning'),
                                                      ('Biology and life sciences',
                                                       'Neuroscience',
                                                       'Learning and memory',
                                                       'Learning',
                                                       'Human learning'),
                                                      ('Computer and information sciences', 'Computer software'),
                                                      ('Physical sciences', 'Physics', 'States of matter', 'Fluids', 'Liquids'),
                                                      ('People and places', 'Population groupings', 'Professions', 'Teachers')],
                                    'heading': [('Community Page',)]}
        assert article.title == "Liquid-handling Lego robots and experiments for STEM education and research"
        assert article.type_ == "other"
        assert article.url == "http://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.2001413&type=manuscript"
        assert article.word_count == 3070

    def test_example_doi2(self):
        """Tests the methods and properties of the Article class
        Test article DOI: 10.1371/annotation/3155a3e9-5fbe-435c-a07a-e9a4846ec0b6
        XML file is in test directory
        """
        article = Article(example_doi2, directory=TESTDATADIR)
        assert article.amendment is True
        assert article.get_aff_dict() == {}
        assert article.get_contributions_dict() == {}
        assert article.get_contributors_info() == [{'contrib_initials': 'LW', 'given_names': 'LingLin', 'surname': 'Wan', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'JH', 'given_names': 'Juan', 'surname': 'Han', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'MS', 'given_names': 'Min', 'surname': 'Sang', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'AL', 'given_names': 'AiFen', 'surname': 'Li', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'HW', 'given_names': 'Hong', 'surname': 'Wu', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'SY', 'given_names': 'ShunJi', 'surname': 'Yin', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'CZ', 'given_names': 'ChengWu', 'surname': 'Zhang', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}]
        assert article.get_corr_author_emails() == {}
        assert article.get_dates() == {'collection': datetime.datetime(2012, 1, 1, 0, 0), 'epub': datetime.datetime(2012, 6, 29, 0, 0), 'updated': ''}
        assert article.get_fn_dict() == {}
        assert article.get_related_dois() == {'retracted-article': ['10.1371/journal.pone.0035142']}
        assert article.get_page(page_type='assetXMLFile') == "http://journals.plos.org/plosone/article/file?id=10.1371/annotation/3155a3e9-5fbe-435c-a07a-e9a4846ec0b6&type=manuscript"
        assert article.abstract[:100] == ""
        assert article.authors == [{'contrib_initials': 'LW', 'given_names': 'LingLin', 'surname': 'Wan', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'JH', 'given_names': 'Juan', 'surname': 'Han', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'MS', 'given_names': 'Min', 'surname': 'Sang', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'AL', 'given_names': 'AiFen', 'surname': 'Li', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'HW', 'given_names': 'Hong', 'surname': 'Wu', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'SY', 'given_names': 'ShunJi', 'surname': 'Yin', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}, {'contrib_initials': 'CZ', 'given_names': 'ChengWu', 'surname': 'Zhang', 'group_name': None, 'ids': [], 'rid_dict': {}, 'contrib_type': 'author', 'author_type': 'contributing', 'editor_type': None, 'email': None, 'affiliations': [], 'author_roles': {}, 'footnotes': []}]
        assert article.corr_author == []
        assert article.amendment is True
        assert article.counts == {}
        assert article.doi == "10.1371/annotation/3155a3e9-5fbe-435c-a07a-e9a4846ec0b6"
        assert article.dtd == "NLM 3.0"
        assert article.editor == []
        article_relpath = os.path.relpath(article.filename, TESTDIR)
        assert article_relpath == "testdata/plos.correction.3155a3e9-5fbe-435c-a07a-e9a4846ec0b6.xml"
        assert article.journal == "PLOS ONE"
        assert article.local is True
        assert article.page == "http://journals.plos.org/plosone/article?id=10.1371/annotation/3155a3e9-5fbe-435c-a07a-e9a4846ec0b6"
        assert article.plostype == "Retraction"
        assert article.proof == ''
        assert article.pubdate == datetime.datetime(2012, 6, 29, 0, 0)
        assert article.related_dois == ["10.1371/journal.pone.0035142"]
        assert article.title[:100] == "Retraction: De Novo Transcriptomic Analysis of an Oleaginous Microalga: Pathway Description and Gene"
        assert article.type_ == "retraction"
        assert article.url[:100] == "http://journals.plos.org/plosone/article/file?id=10.1371/annotation/3155a3e9-5fbe-435c-a07a-e9a4846e"
        assert article.word_count == 129
        assert article.license == {'license': 'CC-BY 4.0', 'license_link': 'https://creativecommons.org/licenses/by/4.0/', 'copyright_holder': '', 'copyright_year': 2012}

    def test_proofs(self):
        """Tests whether uncorrected proofs and VOR updates are being detected correctly."""
        os.environ['PLOS_CORPUS'] = TESTDATADIR
        article = Article(example_uncorrected_doi)
        assert article.proof == 'uncorrected_proof'
        article = Article(example_vor_doi)
        assert article.proof == 'vor_update'
        text_file = os.path.join(TESTDIR, 'test.txt')
        proofs1 = get_uncorrected_proofs(proof_filepath=text_file)
        assert proofs1 == {example_uncorrected_doi}
        proofs2 = check_for_uncorrected_proofs(directory=None, proof_filepath=text_file)
        assert proofs2 == {example_uncorrected_doi}
        os.remove(text_file)


class TestCorpusClass(unittest.TestCase):
    def test_starterdir(self):
        corpus = Corpus(directory=starterdir)
        assert len(corpus.files) == len(listdir_nohidden(starterdir))
        assert set(corpus.filepaths) == set(listdir_nohidden(starterdir))
        assert 'journal.pcbi.0030158.xml' in corpus.files
        assert '10.1371/journal.pmed.0030132' in corpus.dois



if __name__ == "__main__":
    unittest.main()
