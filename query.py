import numpy as np 
import pandas as pd 
from bs4 import BeautifulSoup
import requests 
import time


def nytimes_query(api_key, query, 
                  glocations = None, headline = None, news_desk = None, 
                  organizations = None, persons = None, byline = None, 
                  subject = None, news_type = None, type_of_material = None, 
                  begin_date = None, end_date = None, n_page = 0):
    '''
    Perform a query from the NYTimes API and return a JSON of results
    ----
    Arguments:
    api-key -- a user-specific key registered at developer.nytimes.com
    query -- the search terms used for the query
    
    filters:
        each of the following categories is set at None by default. If values are added, the
        queries will be filtered based on the parameter

        glocations -- geographic locations
        headline -- literal headline
        news_desk -- by news desk using the following values:
            Adventure Sports
            Arts & Leisure
            Arts
            Automobiles
            Blogs
            Books
            Booming
            Business Day
            Business
            Cars
            Circuits
            Classifieds
            Connecticut
            Crosswords & Games
            Culture
            DealBook
            Dining
            Editorial
            Education
            Energy
            Entrepreneurs
            Environment
            Escapes
            Fashion & Style
            Fashion
            Favorites
            Financial
            Flight
            Food
            Foreign
            Generations
            Giving
            Global Home
            Health & Fitness
            Health
            Home & Garden
            Home
            Jobs
            Key
            Letters
            Long Island
            Magazine
            Market Place
            Media
            Men's Health
            Metro
            Metropolitan
            Movies
            Museums
            National
            Nesting
            Obits
            Obituaries
            Obituary
            OpEd
            Opinion
            Outlook
            Personal Investing
            Personal Tech
            Play
            Politics
            Regionals
            Retail
            Retirement
            Science
            Small Business
            Society
            Sports
            Style
            Sunday Business
            Sunday Review
            Sunday Styles
            T Magazine
            T Style
            Technology
            Teens
            Television
            The Arts
            The Business of Green
            The City Desk
            The City
            The Marathon
            The Millennium
            The Natural World
            The Upshot
            The Weekend
            The Year in Pictures
            Theater
            Then & Now
            Thursday Styles
            Times Topics
            Travel
            U.S.
            Universal
            Upshot
            UrbanEye
            Vacation
            Washington
            Wealth
            Weather
            Week in Review
            Week
            Weekend
            Westchester
            Wireless Living
            Women's Health
            Working
            Workplace
            World
            Your Money
        organizations 
        persons -- filter by persons referenced
        byline -- filter by writer or several other parameters- see developer.nytimes.com
        subject -- by subject
        type_of_material -- document type- sample values below:
            Addendum
            An Analysis
            An Appraisal
            Archives
            Article
            Banner
            Biography
            Birth Notice
            Blog
            Brief
            Caption
            Chronology
            Column
            Correction
            Economic Analysis
            Editorial
            Editorial Cartoon
            Editors' Note
            First Chapter
            Front Page
            Glossary
            Interactive Feature
            Interactive Graphic
            Interview
            Letter
            List
            Marriage Announcement
            Military Analysis
            News
            News Analysis
            Newsletter
            Obituary
            Obituary (Obit)
            Op-Ed
            Paid Death Notice
            Postscript
            Premium
            Question
            Quote
            Recipe
            Review
            Schedule
            SectionFront
            Series
            Slideshow
            Special Report
            Statistics
            Summary
            Text
            Video
            Web Log

    date params:
        begin_date -- beginning date of filter 
        end_date -- end date of filter
    n_page -- the selected page of returns- for large queries this will select sections to return
    '''
    # Set the base url for the query
    base_url = f'https://api.nytimes.com/svc/search/v2/articlesearch.json?q={query}'             
    # Empty dictionary for filters
    filter_queries = {}
    # empty dictionary for dates
    dates = {}

    # Populate the filter dictionary
    if glocations:
        filter_queries.update({'glocations': glocations})
    if headline:
        filter_queries.update({'headline': headline})
    if news_desk:
        filter_queries.update({'news_desk': news_desk})
    if organizations:
        filter_queries.update({'organizations': organizations})
    if persons:
        filter_queries.update({'persons': persons})
    if subject:
        filter_queries.update({'subject': subject})
    if byline:
        filter_queries.update({'byline': byline})
    if news_type:
        filter_queries.update({'news_type': news_type})
    if type_of_material:
        filter_queries.update({'type_of_material': type_of_material})
    
    # Populate the date dictionary
    if begin_date:
        dates.update({'begin_date': begin_date})
    if end_date:
        dates.update({'end_date': end_date})
    
    # If 1 filter is present, and/or date params, add to URL and execute query
    if len(filter_queries) == 1:
        base_url += f'&fq={list(filter_queries.keys())[0]}:({list(filter_queries.values())[0]})'
        if len(dates) == 1:
            base_url += f'&{list(filter_queries.keys())[0]}={list(filter_queries.values())[0]}&'
        elif len(dates) == 2:
            base_url += '&'
            for i in dates.keys():
                base_url += f'{i}={dates[i]}&'

    # If 2 or more filters are present, concatenate with AND, add dates if present and execute
    elif  len(filter_queries) > 1:
        base_url += '&fq='
        for i in filter_queries.keys():
            base_url += f'{i}:({filter_queries[i]}) AND '
        base_url = base_url[:-5]
        if len(dates) == 1:
            base_url += f'&{list(filter_queries.keys())[0]}={list(filter_queries.values())[0]}&'
        elif len(dates) == 2:
            base_url += '&'
            for i in dates.keys():
                base_url += f'{i}={dates[i]}&'

    # concatenate page number and api key and make the request. 
    # Returns a truncated JSON indexed past the metadata
    base_url += f'&page={n_page}'
    base_url += f'&api-key={api_key}'
    r = requests.get(base_url)
    json_data = r.json()
    return r.json()['response']['docs']

def review_url_names(api_key, query, n_pages_min, n_pages_max, **kwargs):
    '''Uses nytimes_query as a helper function to return lists of urls, publication dates,
       and formatted restaurant names from a query and specified page range. nytimes_query 
       inherits keyword arguments for specific filters and fields.'''
    
    # instantiate empty lists for each category
    urls = []
    names = []
    dates = []
    
    # iterate through each page in the specified range, getting 10 results per page
    for i in range(n_pages_min, n_pages_max):
        # run the query and hold in a temporary dictionary
        qref = nytimes_query(api_key, query, n_page = i, **kwargs)
        # reformat urls into restaurant name format
        names += [j['web_url'].split('dining/')[1][:-5].replace('-', ' ').replace('reviews/', '') for j in qref]
        # add urls to list
        urls += [k['web_url'] for k in qref]
        # add dates to list
        dates += [m['pub_date'] for m in qref]
        # pause for 6 seconds to avoid going over the max query limit of 60 articles/minute
        time.sleep(6)
    # return lists
    return urls, names, dates

def remove_stopwords(column, stopwords):
    ''''''
    column = column.apply(lambda x: ' '.join([item for item in x.split(' ') if item not in stopwords]))
    return column

def get_stars(list_of_urls):
    ''''''
    stars = []
    for i in list_of_urls:
        page = requests.get(i)
        soup = BeautifulSoup(page.content, 'html.parser')
        l = soup.find(class_="css-z4hz5")
        if l:
            stars.append(l.text)
        else:
            stars.append(np.NaN)
    return stars

def drop_rows(stopwords, dataframe, dataframe_column):
    ''''''
    for i in stopwords:
        dataframe = dataframe[~dataframe[dataframe_column].str.contains(i)]
    return dataframe

def borough_column(address_column):
    ''''''
    borough = []
    for i in address_column:
        borough.append(i.split(', NY')[0].split(' ')[-1])
    for i in range(len(borough)):
        if borough[i] in ('York', 'States'):
            borough[i] = 'Manhattan'
        elif borough[i] in ('Maspeth', 'Ridgewood', 'Astoria', 'Flushing', 
                            'City', 'Hill', 'Broadway', 'Point', 'Park'):    
            borough[i] = 'Queens'
        elif borough[i] == 'Island':
            borough[i] = 'Staten Island'

    return borough