import lxml.etree as et
import re

from .author import Author
from .editor import Editor

from .contributor_elements import (corr_author_emails, get_credit_dict)


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
        # self.match_contribs_to_affs()
        self.match_contribs_to_rids()
        self.corresponding = self.get_corresponding_authors()

    def parse_author_notes(self):
        """Parse footnotes and author notes into email_dict, credit_dict, and id_dict."""

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

        # some 'con'-type elements need to be turned into credit_dict.
        # go through them and turn them into credit_dict or else add to the misc elems.
        # misc_elems will need to be matched to individual authors.
        misc_elems = []
        con_elems = [el for el in fn_elems if el.attrib.get('fn-type') == 'con']
        credit_dict_bool = False
        for con_elem in con_elems:
            if not credit_dict_bool:
                # only try creating the credit dict if it doesn't exist yet
                credit_dict = get_credit_dict(self.doi, con_elem)
                if credit_dict:
                    credit_dict_bool = True
                else:
                    misc_elems.append(con_elem)
            else:
                # credit_dict already exists, so it must be miscellaneous
                misc_elems.append(con_elem)

        fn_misc = [el for el in fn_elems if el.attrib.get('fn-type') not in ['conflict', 'con'] and el.attrib.get('id')]

        # add back the 'con'-type elements that are not making credit_dict, if any
        fn_misc.extend(misc_elems)

        fn_dict = {}
        id_dict = {}
        for el in fn_misc:
            fn_dict = {}
            idd = el.attrib.get('id')
            assert id_dict.get(idd) is None
            elem_text = re.sub('^[^a-zA-z]*|[^a-zA-Z]*$',
                               '',
                               et.tostring(el,
                                           method='text',
                                           encoding='unicode'))
            elem_text = re.sub('[a-z]Current', 'Current', elem_text).lstrip('a').lstrip('b').lstrip('c').strip()
            fn_dict[el.attrib.get('fn-type')] = elem_text
            id_dict[idd] = fn_dict

        # # add key-value pairs in aff_dict to id_dict
        id_dict.update(self.aff_dict)

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

    # def match_contribs_to_affs(self):
    #     """Match the values in self.aff_dict to the rids for each contributor."""
    #     for contrib in self.get_contributors():
    #         contrib.affiliations = []
    #         aff_keys = contrib.rid_dict.get('aff')
    #         if aff_keys:
    #             contrib.affiliations = [self.aff_dict[k] for k in aff_keys]
            # elif self.aff_dict and not contrib['name'].get('group_name', None):  # exclude collabs
                # print('affiliations missing for {}, {}'.format(self.doi, contrib['name']))

    def match_contribs_to_rids(self):
        """Match the footnote values in self.id_dict to the rids for each contributor."""
        for contrib in self.get_contributors():
            contrib.footnotes = {}
            contrib.affiliations = []
            # if contrib.rid_dict.get('fn'):
                # for fn_id in contrib.rid_dict['fn']:
                #     try:
                #         new_id = next(iter(self.id_dict[fn_id].keys()))
                #         if new_id not in contrib.footnotes:
                #             contrib.footnotes[new_id] = [next(iter(self.id_dict[fn_id].values()))]
                #         else:
                #             contrib.footnotes[new_id].append(next(iter(self.id_dict[fn_id].values())))
                #     except KeyError:
                #         # handle the rare cases where footnotes weren't categorized
                #         try:
                #             # first: affiliations
                #             new_id = next(iter(self.aff_dict[fn_id]))
                #             if not hasattr(contrib, 'affiliations'):
                #                 contrib.affiliations = [next(iter(self.id_dict[fn_id].values()))]
                #             else:
                #                 contrib.affiliations.append(next(iter(self.id_dict[fn_id].values())))
                #             print('affiliation updated for {}'.format(self.aff_dict))
                #         except KeyError:
                #             # second: email (for authors only)
                #             try:
                #                 if contrib.contrib_type == 'author':
                #                     new_id = next(iter(self.email_dict[fn_id]))
                #                     assert not contrib.email
                #                     contrib.email = self.email_dict[fn_id]
                #                     print('email updated for {}'.format(self.email_dict))
                #             except KeyError:
                #                 # this can happen if the email field is mult authors
                #                 # ignore the rid in this case
                #                 assert len(self.email_dict) > 1
            for rid, rid_type in contrib.rid_dict.items():
                if rid_type != 'corresp':
                    value = self.id_dict[rid]
                    if rid_type == 'aff':
                        contrib.affiliations.append(value)
                    else:
                        if contrib.footnotes.get(rid_type, None):
                            contrib.footnotes[rid_type].update(value)
                        else:
                            contrib.footnotes[rid_type] = value
            # print(contrib.footnotes, contrib.affiliations)


            # if len(contrib.footnotes) > 1:
            #     print(self.doi, contrib.footnotes)
