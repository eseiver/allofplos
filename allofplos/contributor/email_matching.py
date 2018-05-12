import difflib
import re

import pandas as pd
from unidecode import unidecode


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


def match_to_emails(authors, email_dict):
    """Match the email dictionary emails to each of the authors.
    Follows a set of rules to favor matches for authors that are marked as corresponding.
    Every author is also checked for matching on their initials, the string of their names vs the
    string of the email address. Extra points given for 3+ length initials, when corresponding
    author count matches the length of the email dictionary, and for full name matches.
    The author with the highest score for each email address is assigned that email address.
    """
    corr_author_list = [auth for auth in authors if auth.author_type == 'corresponding']

    # simplest scenario: 1 corresponding author, 1 email (80% of articles)
    if len(corr_author_list) == len(email_dict) == 1:
        matching_error = match_single_email(corr_author_list, email_dict)

    # all other email scenarios
    else:
        author_dict = {auth: (auth.author_type, auth.name.get('initials', '')) for auth in authors}
        match_tuples = []
        for k, v in email_dict.items():
            for key, value in author_dict.items():
                score = 0
                # add score if corresponding author
                if value[0] == 'corresponding':
                    # matters more if the number of emails matches number of corr authors
                    if len(corr_author_list) == len(email_dict):
                        score += 20
                    else:
                        print('author number mismatch for {}'.format(value))
                        score += 3

                # match initials
                if k == value[1]:
                    # if it's three or more characters, it's a very good initials match
                    # ... only if there's one email address associated with it
                    if len(k) > 2 and len(v) == 1:
                        score += 20
                    else:
                        score += 10
                # handle initials case where middle initial missing, and each initials is at least 2 characters
                elif len(k) != len(value[1]) and len(k) >= 2 and len(value[1]) >= 2:
                    new_k = ''.join([k[0], k[-1]])
                    new_value = ''.join([value[1][0], value[1][-1]])
                    if new_k == new_value:
                        score += 5

                # name to email address matching
                # make a separate match for each email address in email_dict
                # make email beginning into same kind of string (i.e., no non-alpha characters)
                name_list = unidecode(key.name.get('given_names', '')).lower().split() + unidecode(key.name.get('surname', '')).lower().split()
                for email in v:
                    seq_2 = unidecode(email.lower().split('@')[0])
                    regex = re.compile('[^a-zA-Z]')
                    seq_2 = regex.sub('', seq_2)

                    # add match score for each name in author's name, with extra weight for a full name match
                    for name in name_list:
                        matcher = difflib.SequenceMatcher(a=name, b=seq_2)
                        partial_match = matcher.find_longest_match(0, len(matcher.a), 0, len(matcher.b))
                        partial_score = partial_match[-1]
                        # give a full name match a serious boost
                        if partial_score == len(name):
                            score += partial_score + 10
                        else:
                            score += partial_score
                    match_tuple = (k, email, key.namestrings[0], value, score)
                    match_tuples.append(match_tuple)
        # this needs to be replaced to use numpy instead of pandas
        # need to have a tiebreaker
        try:
            columns = ['initials', 'email', 'name', 'author_info', 'match_score']
            df = pd.DataFrame(match_tuples, columns=columns)
            pivot = df.pivot(index='name', columns='email', values='match_score')
            email_matches = pivot.idxmax().to_dict()
            for k, v in email_matches.items():
                for auth in authors:
                    if auth.namestring == v:
                        auth.email.append(k)
                        break
            # flag DOIs for match scores that are below 20
            # what to do in this case? see if email matches initials? exclude middle name/initial from namestring?
            # if max(pivot.max().to_dict().values()) < 20:
            #     print(art.doi, pivot)
        except ValueError:
            print("Pandas error", match_tuples)
