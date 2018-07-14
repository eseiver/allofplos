from datetime import datetime as dt


class Dates():
    """For parsing date elements of articles."""

    def __init__(self,
                 pub_elements,
                 hist_element,
                 vor_element,
                 doi,
                 string_=False,
                 string_format='%Y-%m-%d'):
        """Initialize an instance of the dates class."""
        self.pub_elements = pub_elements
        self.hist_element = hist_element
        self.vor_element = vor_element
        self.doi = doi
        self.dates = {}
        self.string_ = string_
        self.string_format = string_format

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

    def get_pub_dates(self):
        """For an individual article, get its publication dates (pubdate).

        :return: dict of date types mapped to datetime objects for that article
        :rtype: {dict}
        """
        for element in self.pub_elements:
            pub_type = element.get('pub-type')
            try:
                date = self.parse_article_date(element)
            except ValueError:
                print('Error getting pubdates for {}'.format(self.doi))
                date = ''
            self.dates[pub_type] = date

    def get_hist_dates(self):
        """For an individual article, get all of its historical dates,
        including submission and acceptance.
        :return: dict of date types mapped to datetime objects for that article
        :rtype: {dict}
        """
        for elem in self.hist_element:
            date_type = elem.get('date-type')
            try:
                date = self.parse_article_date(elem)
            except ValueError:
                print('Error getting history dates for {}'.format(self.doi))
                date = ''
            self.dates[date_type] = date

    def get_vor_dates(self):
        """For an individual article, get date the VOR was published (update to uncorrected proof).
        This field structures dates differently than the other date elements.
        :param string_: whether to return dates as a dictionary of strings
        :param string_format: if string_ is True, the format to return the dates in
        :return: dict of date types mapped to datetime objects for that article
        :rtype: {dict}
        """
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
        self.dates['updated'] = rev_date

    def convert_to_string(self):
        """Convert all dates to strings if desired."""
        if self.string_:
            for key, value in self.dates.items():
                if value:
                    self.dates[key] = value.strftime(self.string_format)

        return self.dates

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
