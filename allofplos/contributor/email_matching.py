
def match_single_email(corr_author, email_dict):
    """When an aricle has a single author, match their rid to their email(s)."""
    corr_author = corr_author[0]
    matching = True
    assert len(email_dict.keys()) == 1
    for k, v in email_dict.items():
        if k in corr_author.rid_dict:
            corr_author.email = v
            break
        elif len(email_dict) == 1:
            corr_author.email = list(email_dict.values())[0]
        else:
            matching = False
            print('one_corr_author error finding email for {} in {}'.format(corr_author, email_dict))
    return matching



def match_to_emails(authors):
    corr_author_list = [contrib for contrib in contrib_dict_list if contrib.get('author_type', None) == 'corresponding']
    if not corr_author_list and email_dict:
        print('Email but no corresponding author found for {}'.format(self.doi))
        # matching_error = True
    if corr_author_list and not email_dict:
        print('Corr emails not found for {}'.format(self.doi))
        matching_error = True
    if len(corr_author_list) == 1:
        matching_error = match_single_email(corr_author_list)
    elif email_dict and len(corr_author_list) > 1 and len(set([tuple(x) for x in email_dict.values()])) > 1:
        corr_author_list, matching_error = match_contribs_to_dicts(corr_author_list,
                                                                   email_dict,
                                                                   contrib_key='email')
    elif len(corr_author_list) > 1:
        if email_dict and (len(email_dict) == 1 or len(set([tuple(x) for x in email_dict.values()])) == 1):
            # if there's only one email address, use it for all corr authors
            for corr_author in corr_author_list:
                corr_author['email'] = list(email_dict.values())[0]
        else:
            matching_error = True
    else:
        corr_author_list = []

    match_error_printed = False
    if email_dict and len(email_dict) > len(corr_author_list) > 0:
            print('Contributing author email included for {}'
                  .format(self.doi))
            match_error_printed = True
    elif email_dict and 1 < len(email_dict) < len(corr_author_list):
        print('{} corresponding author email(s) missing for {}'
              .format(len(corr_author_list) - len(email_dict), self.doi))
        match_error_printed = True

