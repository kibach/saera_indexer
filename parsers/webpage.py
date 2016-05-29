import urllib2
import snowballstemmer
import urlparse
from bs4 import BeautifulSoup
from langdetect import detect
import robotparser


LANGUAGES = {
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'ru': 'Russian',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'it': 'Italian',
    'hr': 'Croatian',
    'mk': 'Macedonian',
    'ar': 'Arabic',
    'fi': 'Finnish',
    'no': 'Norwegian',
    'tr': 'Turkish',
    'pl': 'Polish',
    'sv': 'Swedish',
    'uk': 'Ukrainian',
    'ja': 'Japanese',
    'cs': 'Czech',
    'zh': 'Chinese',
    'kr': 'Korean',
}


class WebPage(object):

    page_url = ''
    parsed_url = None
    contents = ''
    requested = False
    soup = None
    title = ''

    def __init__(self, url):
        self.page_url = url
        self.parsed_url = urlparse.urlparse(url)

    def __normalize_link__(self, link):
        if not link:
            return None
        if link.startswith('//'):
            return self.parsed_url.scheme + ':' + link
        elif link.startswith('/'):
            return self.parsed_url.scheme + '://' + self.parsed_url.hostname + link
        elif link.startswith('http://') or link.startswith('https://'):
            return link
        elif link.startswith('#') or link.startswith('javascript:'):
            return None
        else:
            return urlparse.urljoin(self.page_url, link)

    def request(self):
        try:
            rp = robotparser.RobotFileParser()
            rp.set_url(self.parsed_url.scheme + "://" + self.parsed_url.hostname + "/robots.txt")
            rp.read()
            if not rp.can_fetch("*", self.page_url):
                return False, None
            self.contents = urllib2.urlopen(self.page_url).read()
            self.requested = True
            return True, None
        except Exception, e:
            return False, e

    def require_requested_and_soup(self):
        if not self.requested:
            return False

        if self.soup is None:
            self.soup = BeautifulSoup(self.contents, 'html.parser')
            try:
                self.title = self.soup.title.string
            except:
                self.title = ''
            [s.decompose() for s in self.soup(['style', 'script', '[document]', 'head', 'title'])]

        return True

    def get_domain(self):
        return self.parsed_url.hostname

    def get_title(self):
        if not self.require_requested_and_soup():
            return False

        return self.title

    def get_plaintext(self):
        if not self.require_requested_and_soup():
            return False

        return "".join(self.soup.strings)

    def get_contents(self):
        if not self.requested:
            return False

        return self.contents

    def get_language(self):
        if not self.require_requested_and_soup():
            return False

        return detect(self.get_plaintext())

    def get_encoding(self):
        if not self.require_requested_and_soup():
            return False

        return self.soup.original_encoding

    def get_all_links(self):
        if not self.require_requested_and_soup():
            return False

        def link_generator():
            for link in self.soup.find_all('a'):
                nl = self.__normalize_link__(link.get('href'))
                if nl is not None:
                    yield nl

        return link_generator()

    def get_all_stemmas(self):
        if not self.require_requested_and_soup():
            return False

        stemmer = snowballstemmer.stemmer(LANGUAGES[self.get_language()])
        stemmed = {}
        for word in self.get_plaintext().split():
            sw = stemmer.stemWord(word.lower())
            if sw in stemmed:
                stemmed[sw] += 1
            else:
                stemmed[sw] = 1

        return stemmed

    def get_title_stemmas(self):
        if not self.require_requested_and_soup():
            return False

        stemmer = snowballstemmer.stemmer(LANGUAGES[self.get_language()])
        stemmed = {}
        for word in self.get_title().split():
            sw = stemmer.stemWord(word.lower())
            if sw in stemmed:
                stemmed[sw] += 1
            else:
                stemmed[sw] = 1

        return stemmed
