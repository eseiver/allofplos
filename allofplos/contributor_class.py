from .contributor_elements import corr_author_emails, get_fn_list

class Contributor():
    """Class for authors and editors of PLOS articles.

    This class reconciles and combines contributor information from different
    parts of the article XML tree: <contrib> elements, <aff> (affiliation) elements,
    and the <author-notes> element.
    To initialize this class, Article needs to pass lists and dicts of all three
    of these elements into __init__.
    """
    def __init__(self, doi, contrib_list, aff_dict, author_notes):
        self.doi = doi
        self.contrib_list = contrib_list
        self.aff_dict = aff_dict
        self.author_notes = author_notes

        contrib_keys = ['contrib_initials',
                        'given_names',
                        'surname',
                        'group_name',
                        'ids',
                        'rid_dict',
                        'contrib_type',
                        'author_type',
                        'editor_type',
                        'email',
                        'affiliations',
                        'author_roles',
                        'footnotes'
                        ]

    def parse_author_notes(self):
        """Return tuple of corresponding author info and contributions."""

        corresp_elems = []
        fn_elems = []
        for note in self.author_notes:
            if note.tag == 'corresp':
                corresp_elems.append(note)
            elif note.tag == 'fn':
                fn_elems.append(note)
            else:
                assert note.tag in ['corresp', 'fn']

        email_dict = corr_author_emails(self.doi, corresp_elems)

        con_elem = next(el for el in fn_elems if el.attrib.get('fn-type', None) == 'con')
        contrib_dict = contributions_dict(self.doi, con_elem)

        return email_dict, contrib_dict


class Author(Contributor):
    """Class for authors of PLOS articles.

    Inherits from Contributor class.
    """
    def __init__():
        author_keys = ['contrib_initials',
                        'given_names',
                        'surname',
                        'group_name',
                        'ids',
                        'rid_dict',
                        'contrib_type',
                        'author_type',
                        'email',
                        'affiliations',
                        'author_roles',
                        'footnotes'
                        ]


class Editor(Contributor):
    """ Class for editors of PLOS articles.

    Inherits from Contributor class.
    """
    def __init__():
        edtior_keys = ['contrib_initials',
                       'given_names',
                       'surname',
                        'ids',
                        'rid_dict',
                        'contrib_type',
                        'editor_type',
                        'email',
                        'affiliations',
                        'footnotes'
                        ]

