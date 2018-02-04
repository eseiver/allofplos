from .contributor import Contributor


class Editor(Contributor):
    """ Class for editors of PLOS articles.

    Inherits from Contributor class.
    """
    def __init__(self, contrib_element):
        Contributor.__init__(self, contrib_element, contrib_type='editor')
        self.editor_keys = ['initials',
                           'given_names',
                           'surname',
                           'ids',
                           'rid_dict',
                           'contrib_type',
                           'editor_type',
                           'email',
                           'affiliations',
                           'footnotes',
                           ]

