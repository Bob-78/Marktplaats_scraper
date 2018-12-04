# import libraries
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import re
import csv

# --FIRST, GET A LIST OF ALL THE URLs OF THE ITEMS WE'RE INTERESTED IN

# A function to get the total number of pages (base_page): 
def total_pages(base_page):
    
    print("function total_pages called...")
    
    # query the website and return the html to the variable
    retrieved_html = urllib.request.urlopen(base_page + "1")

    # parse the html using beautiful soup and store in variable
    soup_for_total = BeautifulSoup(retrieved_html, "html.parser")

    # get the total amount of pages out of the soup
    total_pages =  int(soup_for_total.select_one("span[class=last]").text)
    
    print("total number of pages for this base page is: {}".format(total_pages))
    
    # Return the total number as an int
    return total_pages


# a function to construct the urls of the listpages to visit
def append_number(url, page_number):
    
    print("function append_number called...")
    
    # appending the count number to the base page URL
    listpage_url = url + str(page_number)

    print("page url created: {}".format(page_url))
    
    # return the url
    return listpage_url


# A function to get all the relevant car URLs of one page (soup):
def get_page_urls(url, page):

    print("function get_page_urls called...")
    
    # append the page number to the url
    page_url = url + str(page)
    
    print("requesting html from {}".format(page_url))
    
    # query the website and return the html to the variable ‘page’
    html = urllib.request.urlopen(page_url)

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(html, "html.parser")

    # let's throw away the HTML from where the ads start at the bottom of the list 
    # this avoids getting false results in our table (i.e. the ads at the bottom of the list)
    ad_part = soup.find("div", {"class": "row bottom-group search-result bottom-listing listing-cas"})
    for elm in ad_part.find_next_siblings(): 
        elm.extract()
    ad_part.extract()

    # get the raw urls from the soup 
    urls_raw = soup.find_all("a", class_ = "listing-table-mobile-link correlation-link")
        
    # get the clean urls
    urls = [x.get("href") for x in urls_raw]

    print("{} urls received from link above.".format(len(urls))) 
    
    return urls

# a function to get all car page urls from all pages
def get_all_urls(url, number_of_pages):
    
    print("function get_all_urls called...")
    print("will try to get urls from {} pages.".format(number_of_pages))
    
    # create an empty list we can extend
    url_list = list()
    
    # For each page in the range, get the urls on that page and extend our list:
    for x in range(number_of_pages):
        page_urls = get_page_urls(url, x + 1)
        
        # add this page's URLs to our list of urls
        url_list.extend(page_urls)
        
        print("urls from page {} added to url  list".format(x + 1))
            
    print("Total of {} urls received from {} pages".format(len(url_list), number_of_pages))
    
    # return the list of all urls    
    return url_list 


# --SECOND, GO THROUGH THE URL LIST AND SCRAPE THE SUMMARY FOR EACH CAR-- #

# a function to get the details of a car, they are returned as a dictionary
def get_car_details(url):

    print("getting car details from: {}".format(url))

    # query the website and return the html to the variable ‘page’
    html = urllib.request.urlopen(url)

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(html, "html.parser")

    # get the data of the first script tag and convert into a string for string manipulation
    data = str(soup.find("script"))

    # cut the <script> tag and some other things from the beginning and end to get valid JSON
    cut = data[27:-13]

    # encode the data so that the json parser can handle it
    encoded = cut.encode('utf-8')

    # load the data as a json dictionary
    jsoned = json.loads(encoded)
    
    # get the subset of jsoned where the most relevant variables are
    attr_raw = jsoned["a"]["attr"]
    
    # convert all dict values in raw_attr to str if they happen to be lists (some are, some aren't)
    attr = {key: str(value[0]) for key, value in attr_raw.items() if isinstance(value, (list,))}
    
    # add prijs (from another part of jsoned) to attr
    attr["Prijs"] = int(jsoned["a"]["prc"]["amt"])/100 # divide by 100 because contains two extra zeros, make int
    # add merk (from another part of jsoned) to attr
    attr["Merk"] = jsoned["c"]["c"]["n"]
    
    # make a list of each value in attr
    for key in attr: 
        attr[key] = [attr[key]]
    
    print("returning attr: {}".format(attr))
    
    return attr

# a function to add the car details to a dataframe
def add_car_results_to_df(df, attr):
    
    print("Function add_car_results_to_df called")
    
    df = df.append(attr, ignore_index=True)
    
    print("data added to df: {}".format(df))
    
    return df


def main_function(base_url, pages):

    all_urls = get_all_urls(base_url, pages)

    df = pd.DataFrame()

    for ad_url in all_urls:
    
        details = get_car_details(ad_url) # this returns a dictionary all_urls[22] for single entry

        df = add_car_results_to_df(df, details)

    df.to_csv('newfilename.csv', sep=';', index=False)

# define base URL, the format should end with "currentpage="
base_url = "https://www.marktplaats.nl/z/auto-s/ferrari/ferrari.html?query=ferrari&categoryId=110&currentPage="

main_function(base_url, 2)
