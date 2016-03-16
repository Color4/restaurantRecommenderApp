#  Trying out beautiful soup for scraping data
import requests, re, urllib2, time
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
import pandas as pd

def getReviews(df, url, offset):
    url2 = url + "?start=%d" % (offset)
    request = urllib2.urlopen(url2)
    soup = BeautifulSoup(request, "lxml")
    letters = soup.find_all("div", class_="review-content")
    reviews = defaultdict(list)
    for element in letters:
        reviews['review'].append(element.p.get_text())
        reviews['rating'].append(float((re.findall('\d+\.\d+', element.i["title"] ))[0]))
        reviews['date'].append(element.span.find("meta")['content'])

    reviewsDf = pd.DataFrame.from_dict(reviews)
    df = pd.concat([df, reviewsDf])
    if len(reviewsDf)<20:
        return df
    else:
        time.sleep(1.0)
        return getReviews(df, url, offset+20)

    
url = "https://www.yelp.com/biz/bandung-indonesian-restaurant-madison"
df = pd.DataFrame(columns=('date', 'rating', 'review'))
reviewsDf = getReviews(df, url, 0)
## bayesian averaging!!
## def getScore(reviews):
    
