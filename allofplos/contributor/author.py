from .contributor import Contributor

author_keys = ['initials',
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
               'footnotes',
               ]


class Author(Contributor):
    """Class for authors of PLOS articles.

    Inherits from Contributor class.
    """
    def __init__(self, contrib_element):
        Contributor.__init__(self, contrib_element, contrib_type='author')
        self.author_type = None
        self.get_author_type()
        self.credit_dict = None
        self.get_credit_taxonomy()
        self.email = None

    def get_author_type(self):
        """Get the type of author for a single contributor from their accompanying <contrib> element.
        Authors can be 'corresponding' or 'contributing'. Depending on the paper, some elements have a 
        top-level "corresp" attribute that equal yes; otherwise, corresponding status can be inferred
        from the existence of the <xref> attribute ref-type="corresp"
        :return: author type (corresponding, contributing, None)
        """
        answer_dict = {
            "yes": "corresponding",
            "no": "contributing"
        }

        author_type = None
        corr = self.contrib_element.get('corresp', None)
        if corr:
            author_type = answer_dict.get(corr, None)
        else:
            temp = self.rid_dict.get('corresp', None)
            if temp:
                author_type = answer_dict.get("yes", None)
            else:
                author_type = answer_dict.get("no", None)

        self.author_type = author_type

    def get_credit_taxonomy(self):
        """Get the contributor roles from the CREDiT taxonomy element when it is present.
        Right now, this is is equivalent to author roles.
        For more information about this data structure, see http://dictionary.casrai.org/Contributor_Roles
        :param contrib_element: An article XML element with the tag <contrib>
        :return: dictionary of contributor roles for an individual contributor

        """
        credit_dict = {}
        for item in self.contrib_element.getchildren():
            if item.tag == 'role':
                content_type = item.attrib.get('content-type', None)
                if content_type == 'http://credit.casrai.org/':
                    content_type = 'CASRAI CREDiT taxonomy'
                role = item.text
                if not credit_dict.get(content_type, None):
                    credit_dict[content_type] = [role]
                else:
                    credit_dict[content_type].append(role)
        self.credit_dict = credit_dict

