import lxml.etree as et
import re

from .author import Author
from .editor import Editor

from .contributor_elements import (corr_author_emails, get_credit_dict, match_contribs_to_dicts,
                                   )


class ContributorList():
    """Class for the collection of authors and editors of PLOS articles.

    This class reconciles and combines contributor information from different
    parts of the article XML tree: <contrib> elements, <aff> (affiliation) elements,
    and the <author-notes> element.
    To initialize this class, Article needs to pass lists and dicts of all three
    of these elements into __init__.
    """
    def __init__(self, contrib_elems, aff_dict, author_notes, doi=''):
        self.doi = doi
        self.contrib_elems = contrib_elems
        self.aff_dict = aff_dict
        self.author_notes = author_notes
        self.email_dict = None
        self.credit_dict = None
        self.id_dict = None
        self.parse_author_notes()
        self.authors = None
        self.editors = None
        self.get_contributors()
        self.match_contribs_to_fns()

    def parse_author_notes(self):
        """Return tuple of corresponding author info and credit for their contributions."""

        corresp_elems = []
        fn_elems = []
        credit_dict = {}
        for elem in self.author_notes:
            for note in elem:
                if note.tag == 'corresp':
                    corresp_elems.append(note)
                elif note.tag == 'fn':
                    fn_elems.append(note)
                else:
                    assert note.tag in ['corresp', 'fn']

        email_dict = corr_author_emails(self.doi, corresp_elems)

        con_elem = next((el for el in fn_elems if el.attrib.get('fn-type') == 'con'), None)
        if con_elem is not None:
            credit_dict = get_credit_dict(self.doi, con_elem)

        fn_misc = [el for el in fn_elems if el.attrib.get('fn-type') != 'conflict' and el.attrib.get('id')]
        fn_dict = {}
        id_dict = {}
        for el in fn_misc:
            idd = el.attrib.get('id')
            assert id_dict.get(idd) is None
            fn_dict[el.attrib.get('fn-type')] = re.sub('^[^a-zA-z]*|[^a-zA-Z]*$',
                                                       '',
                                                       et.tostring(el,
                                                                   method='text',
                                                                   encoding='unicode'))
            id_dict[idd] = fn_dict

        self.email_dict = email_dict
        self.credit_dict = credit_dict
        self.id_dict = id_dict


    def get_contributors(self):
        if self.authors is None and self.editors is None:
            author_list = []
            editor_list = []
            for contrib_elem in self.contrib_elems():
                if contrib_elem.attrib.get('contrib-type') == 'author':
                    author_list.append(Author(contrib_elem))
                elif contrib_elem.attrib.get('contrib-type') == 'editor':
                    editor_list.append(Editor(contrib_elem))
                else:
                    assert contrib_elem.attrib.get('contrib-type') in ['author', 'editor']
            self.authors = author_list
            self.editors = editor_list
        return self.authors + self.editors

    def get_corresponding_authors(self):
        return [auth for auth in self.authors if auth.author_type == 'corresponding']

    def match_contribs_to_affs(self):
        """Match the values in self.aff_dict to the rids for each contributor."""
        for contrib in self.get_contributors():
            aff_keys = contrib.rid_dict.get('aff')
            contrib.aff_list = [self.aff_dict[k] for k in aff_keys]

    def match_contribs_to_fns(self):
        """Match the footnote values in self.id_dict to the rids for each contributor."""
        for contrib in self.get_contributors():
            contrib.footnotes = {}
            if contrib.rid_dict.get('fn'):
                for fn_id in contrib.rid_dict['fn']:
                    try:
                        new_id = next(iter(self.id_dict[fn_id].keys()))
                        assert new_id not in contrib.footnotes
                        contrib.footnotes.update(self.id_dict[fn_id])
                    except KeyError:
                        # handle the rare cases where footnotes weren't categorized
                        try:
                            # first: affiliations
                            new_id = next(iter(self.aff_dict[fn_id]))
                            contrib.affiliations = self.aff_dict[fn_id]
                            print('affiliation updated for {}'.format(self.aff_dict))
                        except KeyError:
                            # second: email (for authors only)
                            try:
                                if contrib.contrib_type == 'author':
                                    new_id = next(iter(self.email_dict[fn_id]))
                                    assert not contrib.email
                                    contrib.email = self.email_dict[fn_id]
                                    print('email updated for {}'.format(self.email_dict))
                            except KeyError:
                                # this can happen if the email field is mult authors
                                # ignore the rid in this case
                                assert len(self.email_dict) > 1









