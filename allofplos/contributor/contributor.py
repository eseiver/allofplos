import lxml.etree as et
import re
import string

contrib_keys = ['initials',
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


class Contributor():
    """An individual contributor on a PLOS article.

    Instantiated with <contrib> element by Contributor_Group class."""
    def __init__(self, contrib_element, contrib_type=None):
        self.contrib_element = contrib_element
        self.contrib_type = contrib_type
        if self.contrib_type is None:
            self.contrib_type = self.contrib_element.attrib['contrib-type']
        self.rid_dict = None
        self.compute_rid_dict()
        self.name = None
        self.get_name()
        self.ids = None
        self.get_ids()

    def __getitem__(self, key):
        return self.__dict__[key]

    def compute_rid_dict(self):
        """ For an individual contributor, get the list of their associated rids.

        More about rids: https://jats.nlm.nih.gov/archiving/tag-library/1.1/attribute/rid.html
        Used in get_contrib_info().
        :return: dictionary matching each type of rid to its value for that contributor
        """
        rid_dict = {}
        subelems = self.contrib_element.getchildren()
        # get list of ref-types
        rid_types = set([el.attrib.get('ref-type', 'fn') for el in subelems if el.tag == 'xref'])

        # make dict of ref-types to the actual ref numbers (rids)
        for rid_type in rid_types:
            rid_list = [el.attrib.get('rid', None) for el in subelems if el.tag == 'xref' and el.attrib.get('ref-type', 'fn') == rid_type]
            rid_dict[rid_type] = rid_list

        # getting aff in the right place if ref-type is missing
        for k, v in rid_dict.items():
            if k != 'aff':
                aff_items = [item for item in v if item.startswith('aff')]
                if aff_items:
                    print('missing ref-type for affiliation item')
                    if rid_dict.get('aff', None):
                        rid_dict['aff'].extend(aff_items)
                    else:
                        rid_dict['aff'] = aff_items
                    rid_dict[k] = [item for item in v if not item.startswith('aff')]

        self.rid_dict = rid_dict

    def get_name(self):
        """Get the name for a single contributor from their accompanying <contrib> element.
        Also constructs their initials for later matching to article-level dictionaries about
        contributors, including aff_dict() and get_fn_dict().
        Can also handle 'collab' aka group authors with a group name but no surname or given names.
        :param contrib_element: An article XML element with the tag <contrib>
        :return: dictionary of a single contributor's given names, surname, initials, and group name
        """
        given_names = ''
        surname = ''

        contrib_name_element = self.contrib_element.find("name")
        if contrib_name_element is not None:
            for name_element in contrib_name_element.getchildren():
                if name_element.tag == 'surname':
                    # for some reason, name_element.text doesn't work for this element
                    surname = (et.tostring(name_element,
                                           encoding='unicode',
                                           method='text').rstrip(' ').rstrip('\t').rstrip('\n')
                               or "")
                elif name_element.tag == 'given-names':
                    given_names = name_element.text
                    if given_names == '':
                        print("given names element.text didn't work")
                        given_names = (et.tostring(name_element,
                                                   encoding='unicode',
                                                   method='text').rstrip(' ').rstrip('\t').rstrip('\n')
                                       or "")
                else:
                    pass
            if given_names or surname:
                # construct initials if either given or surname is present
                try:
                    initials = ''.join([part[0].upper() for part in re.split('[-| |,|\.]+', given_names) if part]) + \
                                      ''.join([part[0] for part in re.split('[-| |,|\.]+', surname) if part[0] in string.ascii_uppercase])
                except (IndexError, TypeError) as e:
                    initials = ''
                contrib_name = dict(initials=initials,
                                    given_names=given_names,
                                    surname=surname)
        else:
            # if no <name> element found, assume it's a collaboration
            contrib_collab_element = self.contrib_element.find("collab")
            group_name = et.tostring(contrib_collab_element, encoding='unicode')
            group_name = re.sub('<[^>]*>', '', group_name).rstrip('\n')
            if not group_name:
                print("Error constructing contrib_name group element")
                group_name = ''
            contrib_name = dict(group_name=group_name)

        self.name = contrib_name

    def get_ids(self):
        """Get the ids for a single contributor from their accompanying <contrib> element.
        This will mostly get ORCID IDs, and indicate whether they are authenticated.
        For more information of ORCIDs, see https://orcid.org/
        :param contrib_element: An article XML element with the tag <contrib>
        :return: list of dictionaries of ids for that contributor
        """
        id_list = []
        for item in self.contrib_element.getchildren():
            if item.tag == 'contrib-id':
                contrib_id_type = item.attrib.get('contrib-id-type', None)
                contrib_id = item.text
                contrib_authenticated = item.attrib.get('authenticated', None)
                id_dict = dict(id_type=contrib_id_type,
                               id=contrib_id,
                               authenticated=contrib_authenticated
                               )
                id_list.append(id_dict)

        return id_list

