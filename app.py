from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import time
from datetime import date
import re

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition

class ResultsPrinter:
    def format_body(self, links):
        body = []
        for link in links:
            body.append('<li><a href=\"{}\">{}</a></li>'.format(*link))
        return body

    def format_html(self, body):
        template = '''
        <!DOCTYPE html>
            <html>
              <head>
                <title>{}</title>
              </head>
              <body>
                <ol>
                {}
                </ol>
              </body>
            </html>
        '''.format('-'.join(['Results ', self.today]),'\n'.join(body))
        return template

    def print_result(self, page):
        file = ''.join([self.path,'results-', self.today,self.extension])
        new = open(file, 'w')
        new.close()
        with open(file,'a') as f:
          print(page, file=f)

    def present_results(self, parsedLinks):
        self.path = './results/'
        self.extension = '.html'
        self.today = date.today().isoformat()
        i = 0
        full_results = self.format_html(self.format_body(parsedLinks))
        self.print_result(full_results)



class LinkParser(HTMLParser):
    def handle_endtag(self, tag):
        if tag == 'a':
            self.flag_for_data = -1

    def handle_data(self, data):
        if (self.flag_for_data != -1):
            self.links_inner_html.insert(self.flag_for_data, data)

    def keyword_filter(self, words, link):
        is_valid = True
        quality = 0
        if self.matcher.search(words):
            formatted_words = words.lower().split()
            for word in formatted_words:
                if is_valid == True:
                    is_valid = (word not in self.not_keywords)
                    if word in self.must_keywords:
                        quality = quality + 1
            if quality > 0:
                print('check')
                return (link, words)
            else:
                return None
        else:
            return None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if (key == 'href' and (value.find('job') != -1)):
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]
                    self.flag_for_data = len(self.links) - 1

    def getLinks(self, url, yes_words, no_words):
        self.must_keywords = yes_words
        self.not_keywords = no_words
        self.matcher = re.compile('develop(er|ment)|engineer', re.IGNORECASE)
        self.links = []
        self.flag_for_data = -1
        self.links_inner_html = []
        self.baseUrl = url
        response = urlopen(url)
        print(response.getheader('Content-Type').find('text/html'))
        if response.getheader('Content-Type').find('text/html') != -1:
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            i = 0
            result = []
            while i < len(self.links):
                new_link = self.keyword_filter(self.links_inner_html[i], self.links[i])
                if new_link:
                    result = result + [new_link]
                i += 1
            return result
        else:
            return None

def main():
    search_terms = {'front-end', 'frontend', 'javascript', 'associate', 'junior', 'software', 'python', 'ruby', 'rails', 'back-end', 'backend', 'web', 'apprentice'}
    not_terms = {'senior', 'architect', 'lead', 'sales'}
    # pagesToVisit = [put it hereee]
    links = []
    #INDEED
    #pages = [""]
    #front_door_url = https://www.indeed.com/recommendedjobs?
    #rootDomain = ""

    #BUILT IN
    pages = ["1","2","3","4","5","6","7"]
    front_door_url = "http://www.builtinchicago.org/jobs?page="
    rootDomain = "http://www.builtinchicago.org"

    for page in pages:
        current_url = "".join([front_door_url, page])
        try:
            parser = LinkParser()
            links = links + parser.getLinks(current_url, search_terms, not_terms)
            print(" **Success!**")
        except:
            print(" **Failed!**")
    printer = ResultsPrinter()
    printer.present_results(links)
    print('woot')

if __name__ == '__main__':
  main()
