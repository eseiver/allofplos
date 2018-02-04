import re

import lxml.etree as et


def corr_author_emails(doi, corresp_list):
    """For an article, grab the email addresses of the corresponding authors.
    Parses the list of emails and groups by rid or by initials, if present.
    Can handle multiple emails for multiple authors if formatted correctly.
    The email addresses are in an element of author notes. While most articles have one corresponding
    author with one email address, sometimes there are 1) multiple authors, and/or 2) multiple emails per
    author. In the first case, author initials are used in the text to separate emails. In the second case,
    a comma is used to separate emails. Initials are how emails can be matched to multiple
    authors. See also `match_author_names_to_emails()` for the back-up method of name matching.
    :param corresp_list: list of elements in <author-notes> with tag 'corresp'
    :return: dictionary of rid or author initials mapped to list of email address(es)
    :rtype: {dict}
    """
    corr_emails = {}
    email_list = []
    for elem in corresp_list:
        author_info = elem.getchildren()
        for i, item in enumerate(author_info):
            # if author initials are in the same field as email address
            if item.tag == 'email' and item.text and all(x in item.text for x in ('(', ')')):
                email_info = item.text.split(' ')
                for i, info in enumerate(email_info):
                    # prune out non-letters from initials & email
                    email_info[i] = re.sub(r'[^a-zA-Z0-9=@\.+-]', '', info)
                try:
                    corr_emails[email_info[1]] = [email_info[0]]
                except IndexError:
                    print('Error parsing emails for {}'.format(doi))

            # if no author initials (one corr author)
            elif item.tag == 'email' and item.tail is None and item.text:
                email_list.append(item.text)
                if item.text == '':
                    print('No email available for {}'.format(doi))
                if elem.attrib['id']:
                    corr_emails[elem.attrib['id']] = email_list
                else:
                    corr_emails['cor001'] = email_list

            # if more than one email per author; making sure no initials present (comma ok)
            elif item.tag == 'email' and re.sub(r'[^a-zA-Z0-9=]', '', str(item.tail)) is None:
                try:
                    if author_info[i+1].tail is None:
                        email_list.append(item.text)
                    elif author_info[i+1].tail:
                        corr_initials = re.sub(r'[^a-zA-Z0-9=]', '', author_info[i+1].tail)
                        if not corr_emails.get(corr_initials):
                            corr_emails[corr_initials] = [item.text]
                        else:
                            corr_emails[corr_initials].append(item.text)
                except IndexError:
                    email_list.append(item.text)
                    corr_emails[elem.attrib['id']] = email_list
                    if i > 1:
                        print('Error handling multiple email addresses for {} in {}'
                              .format(et.tostring(item), doi))
                if item.text == '':
                    print('No email available for {}'.format(doi))

            # if author initials included (more than one corr author)
            elif item.tag == 'email' and item.tail:
                corr_email = item.text
                corr_initials = re.sub(r'[^a-zA-Z0-9=]', '', item.tail)
                if not corr_initials:
                    try:
                        corr_initials = re.sub(r'[^a-zA-Z0-9=]', '', author_info[i+1].tail)
                    except (IndexError, TypeError) as e:
                        corr_initials = elem.attrib['id']
                        if not corr_initials:
                            print('email parsing is weird for', doi)
                if not corr_emails.get(corr_initials):
                    corr_emails[corr_initials] = [corr_email]
                else:
                    corr_emails[corr_initials].append(corr_email)
            else:
                pass
    if not corr_emails:
        for corresp in corresp_list:
            author_notes_field = et.tostring(corresp, method='text', encoding='unicode')
            if '@' in author_notes_field:
                regex_email = r'[\w\.-]+@[\w\.-]+'
                email_finder = re.compile(regex_email)
                email_list = email_finder.findall(author_notes_field)
                if email_list:
                    corr_emails['cor001'] = email_list
                    break
    return corr_emails


def get_fn_list(fn_list):
    """For a given article's list of footnote elements, turn them into a list of dicts.

    Used with rids to map individual contributors to their institutions
    More about rids: https://jats.nlm.nih.gov/archiving/tag-library/1.1/attribute/rid.html
    See also get_rid_dict()
    Use IDs as the mapping whenever able to
    :returns: Dictionary of footnote ids to institution information
    :rtype: {dict}
    """

    new_fn_list = []
    for el in fn_list:
        # idd = el.attrib.get('id', None)
        el_text = et.tostring(el,
                              method='text',
                              encoding='unicode').strip().replace('\n', '').replace('\r', '').replace('\t', '')
        fn_dict = {}
        fn_dict = {k: v for k, v in el.attrib.items()}
        fn_dict['content'] = el_text
        new_fn_list.append(fn_dict)
    return new_fn_list


def get_credit_dict(doi, con_elem):
    """For articles that don't use the CREDiT taxonomy, compile a dictionary of author
    contribution types matched to author initials.
    Work in progress!!
    Works for highly formatted lists with subelements (e.g. '10.1371/journal.pone.0170354') and structured single strings
    (e.g. '10.1371/journal.pone.0050782'), but still fails for unusual strings (e.g, '10.1371/journal.pntd.0000072')
    See also get_credit_taxonomy() for the CREDiT taxonomy version.
    TODO: Use regex to properly separate author roles from initials for unusual strings.
    :return: dictionary mapping author initials to their author contributions/roles.
    """
    author_contributions = {}
    contrib_dict = {}
    initials_list = []
    regex = re.compile('[^a-zA-Z]')
    try:
        # for highly structured lists with sub-elements for each item
        # Example: 10.1371/journal.pone.0170354'
        sub_el = con_elem[0][0]
        if sub_el.attrib.get('list-type'):
            con_list = sub_el.getchildren()
            for con_item in con_list:
                contribution = con_item[0][0].text.rstrip(':')
                contributor_initials = (con_item[0][0].tail.lstrip(' ').rstrip('.')).split(' ')
                contributor_initials = [regex.sub('', v) for v in contributor_initials]
                initials_list.extend(contributor_initials)
                contrib_dict[contribution] = contributor_initials

    except IndexError:
        # for single strings, though it doesn't parse all of them correctly.
        # Example: '10.1371/journal.pone.0050782'
        contributions = con_elem[0].text
        if contributions is None:
            contributions = et.tostring(con_elem,
                                        encoding='unicode',
                                        method='text')
            contrib_dict = {}  # reset because it was probably an error during parsing
        contributions = contributions.lstrip('The author(s) have made the following declarations about their contributions: ')
        # Placeholder for when the contribs are written as sentences
        # if contributions[:2] == contributions[:2].upper():
        #     print(contributions.split('.'))
        contribution_list = re.split(': |\. ', contributions)
        contribb_dict = dict(list(zip(contribution_list[::2], contribution_list[1::2])))
        for k, v in contribb_dict.items():
            v_new = v.split(' ')
            v_new = [regex.sub('', v) for v in v_new]
            contrib_dict[k.strip('\n')] = v_new
            initials_list.extend(v_new)

    # Re-do dictionary so it's by initials instead of by role
    # if [x[:4] for x in initials_list] != initials_list:
    #     print(doi, initials_list)

    for initials in (set(initials_list)):
        contrib_list = []
        for k, v in contrib_dict.items():
            if initials in v:
                contrib_list.append(k)
        author_contributions[initials] = contrib_list
    return author_contributions