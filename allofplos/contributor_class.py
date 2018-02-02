from .contributor_elements import corr_author_emails, get_fn_list

class Contributor():
    """Class for authors and editors of PLOS articles.

    This class reconciles and combines contributor information from different
    parts of the article XML tree: <contrib> elements, <aff> (affiliation) elements,
    and the <author-notes> element.
    To initialize this class, Article needs to pass lists and dicts of all three
    of these elements into __init__.
    """
    def __init__(self, doi, contrib_list, aff_dict, fn_list, corresp_elems):
        self.doi = doi
        self.contrib_list = contrib_list
        self.aff_dict = aff_dict
        self.fn_list = fn_list
        self.corresp_elems = corresp_elems

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
        """Return tuple of into footnotes and corresponding author info"""
        email_dict = corr_author_emails(self.doi, self.corresp_elems)

        fn_id_list = [x.get('id', None) for x in self.fn_list]

        return email_dict.keys(), fn_id_list


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

