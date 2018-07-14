from datetime import datetime as dt


class Dates():
    """For parsing date elements of articles."""

    def __init__(self, date_element, doi):
        """Initialize an instance of the dates class."""
        self.element = date_element
        self.doi = doi

    def parse_article_date(date_element, date_format='%d %m %Y'):
        """
        For an article date element, convert XML to a datetime object.
        :param date_element: An article XML element that contains a date
        :param date_format: string format used to convert to datetime object
        :return: datetime object
        """
        day = ''
        month = ''
        year = ''
        for item in date_element.getchildren():
            if item.tag == 'day':
                day = item.text
            if item.tag == 'month':
                month = item.text
            if item.tag == 'year':
                year = item.text
        if day:
            date = (day, month, year)
            string_date = ' '.join(date)
            date = dt.strptime(string_date, date_format)
        elif month:
            # try both numerical & word versions of month
            date = (month, year)
            string_date = ' '.join(date)
            try:
                date = dt.strptime(string_date, '%m %Y')
            except ValueError:
                date = dt.strptime(string_date, '%B %Y')
        elif year:
            date = year
            date = dt.strptime(date, '%Y')
        else:
            print('date error')
            date = ''
        return date

    def get_dates(self, string_=False, string_format='%Y-%m-%d'):
        """For an individual article, get all of its dates, including publication date (pubdate), submission date.

        Defaults to datetime objects
        :param string_: whether to return dates as a dictionary of strings
        :param string_format: if string_ is True, the format to return the dates in
        :return: dict of date types mapped to datetime objects for that article
        :rtype: {dict}
        """
        dates = {}
        # first location is where pubdate and date added to collection are
        tag_path_1 = ["/",
                      "article",
                      "front",
                      "article-meta",
                      "pub-date"]
        element_list_1 = self.get_element_xpath(tag_path_elements=tag_path_1)
        for element in element_list_1:
            pub_type = element.get('pub-type')
            try:
                date = self.parse_article_date(element)
            except ValueError:
                print('Error getting pubdates for {}'.format(self.doi))
                date = ''
            dates[pub_type] = date

        # second location is where historical dates are, including submission and acceptance
        tag_path_2 = ["/",
                      "article",
                      "front",
                      "article-meta",
                      "history"]
        element_list_2 = self.get_element_xpath(tag_path_elements=tag_path_2)
        for element in element_list_2:
            for part in element:
                date_type = part.get('date-type')
                try:
                    date = self.parse_article_date(part)
                except ValueError:
                    print('Error getting history dates for {}'.format(self.doi))
                    date = ''
                dates[date_type] = date

        # third location is for vor updates when it's updated (see `proof(self)`)
        rev_date = ''
        if self.proof == 'vor_update':
            tag_path = ('/',
                        'article',
                        'front',
                        'article-meta',
                        'custom-meta-group',
                        'custom-meta')
            xpath_results = self.get_element_xpath(tag_path_elements=tag_path)
            for result in xpath_results:
                if result.xpath('./meta-name')[0].text == 'Publication Update':
                    rev_date_string = result.xpath('./meta-value')[0].text
                    rev_date = dt.strptime(rev_date_string, '%Y-%m-%d')
                    break
                else:
                    pass
        dates['updated'] = rev_date

        if string_:
            # can return dates as strings instead of datetime objects if desired
            for key, value in dates.items():
                if value:
                    dates[key] = value.strftime(string_format)

        return dates

    def dates_debug(self):
        """Whether the dates in self.get_dates() are in the correct order.

        check whether date received is before date accepted, is before pubdate
        accounts for potentially missing date fields
        :return: if dates are in right order or not
        :rtype: bool
        """
        dates = self.get_dates()
        if dates.get('received', '') and dates.get('accepted', ''):
            if dates['received'] <= dates['accepted'] <= dates['epub']:
                order_correct = True
            else:
                order_correct = False
        elif dates.get('received', ''):
            if dates['received'] <= dates['epub']:
                order_correct = True
            else:
                order_correct = False
        elif dates.get('accepted', ''):
            if dates['accepted'] <= dates['epub']:
                order_correct = True
            else:
                order_correct = False
        else:
            order_correct = True

        return order_correct
