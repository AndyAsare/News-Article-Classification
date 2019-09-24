import requests
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup

list = ['politics', 'business', 'health', 'technology', 'entertainment']
cbc = 'https://www.cbc.ca/news/'

with open('news.csv', 'a+') as csvFile:
    writer = csv.writer(csvFile)
    for i in range(1, 6):
        request = requests.get(cbc + list[i-1]) # Obtain the html code of https://www.cbc.ca/news/(desired category)
        soup = BeautifulSoup(request.text, "html5lib") # Remove most of the html tags
        text = soup.get_text()

        try:
            found = re.findall('{"imageAspects":(.+?)"category":', text) # a list of news article and its information, with some html tags remain
        except AttributeError:
            found = []

        for piece in found:
            externality = re.findall('"external":(.+?),"flag"', piece)[0] # check if this is an external article (we won't use those articles)
            if externality == 'false':
                title_long = re.findall('updateTime":(.+?)source":"', piece)[0] # obtain the title: step 1
                title = re.findall('title":"(.+?)","', title_long)[0] # obtain the title: step 2
                
                link = re.findall('itemURL":"(.+?)","description', piece)[0]
                link_processed = link.replace("u002F", "")
                link_processed = link_processed.replace("\\", "/") # extract the link for each news article, and apply web-scraping on those pages instead
                
                r = requests.get(link_processed)
                text = BeautifulSoup(r.text, "html5lib").get_text()
                body = re.findall('body":"(.+?)","keywords', text)[0]

                try:
                    hyperlink = re.findall('u003C(.+?)u003E', body)
                except AttributeError:
                    hyperlink = []

                for char in hyperlink:
                    body = body.replace("u003C" + char + "u003E", "") # remove html tags in the articles, mostly hyperlinks
                
                body = body.replace("[IMAGE]", "")
                body = body.replace("[EMBED]", "")
                body = body.replace("[MEDIA]", "")
                body = body.replace("\\", "")
                body = body.replace("[SIMILAR]", "")
                body = body.replace("&nbsp;", " ")
                row = ['0', title, body, list[i-1]]
                writer.writerow(row) # write into the csv file

csvFile.close()

df = pd.read_csv('news.csv', index_col=0)
df.columns = ['title', 'content', 'category']
df.drop_duplicates('title', keep='last', inplace=True) # drop repeated articles
df.reset_index(inplace=True, drop=True)
df.to_csv('news.csv')
