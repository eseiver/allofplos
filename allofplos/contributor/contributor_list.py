from .author import Author
from .editor import Editor

from .contributor_elements import corr_author_emails, get_credit_dict


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
        self.parse_author_notes()
        self.authors = None
        self.editors = None
        self.get_contributors()

    def parse_author_notes(self):
        """Return tuple of corresponding author info and credit for their contributions."""

        corresp_elems = []
        fn_elems = []
        credit_dict = {}
        for note in self.author_notes:
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

        self.email_dict = email_dict
        self.credit_dict = credit_dict

    def get_contributors(self):
        author_list = []
        editor_list = []
        for contrib_elem in self.contrib_elems():
            if contrib_elem.attrib['contrib-type'] == 'author':
                author_list.append(Author(contrib_elem))
            if contrib_elem.attrib['contrib-type'] == 'editor':
                editor_list.append(Editor(contrib_elem))
        self.authors = author_list
        self.editors = editor_list




