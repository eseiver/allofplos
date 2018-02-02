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
