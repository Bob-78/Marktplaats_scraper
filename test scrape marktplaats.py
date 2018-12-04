# import libraries
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
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
    for elm in ad_part.find_next_siblings(): # from tag ad part, go to the end of the document
        elm.extract() # delete each element
    ad_part.extract() # delete the ad part itself

    # get the raw urls from the soup 
    urls_raw = soup.find_all("a", class_ = "listing-table-mobile-link correlation-link") #this still contains htmls tags etc.
        
    # get the clean urls
    urls = [x.get("href") for x in urls_raw]

    print("{} urls received from link above.".format(len(urls))) 
    
    return urls

# a function to build a list of all ad page urls
def get_all_urls(url, number_of_pages):
    
    print("function get_all_urls called...")
    print("will try to get urls from {} pages.".format(number_of_pages))
    
    # create an empty list we can extend
    url_list = list()
    
    # For each page in the range, get the urls on that page and extend our list:
    for x in range(number_of_pages):
        page_urls = get_page_urls(url, x + 1) # this first number in the range is 0, so x+1 has us start at the first page
        
        # add this page's URLs to our list of urls
        url_list.extend(page_urls)
        
        print("urls from page {} added to url  list".format(x + 1))
            
    print("Total of {} urls received from {} pages".format(len(url_list), number_of_pages))
    
    # return the list of all urls    
    return url_list 


# --SECOND, GO THROUGH THE URL LIST AND SCRAPE THE SUMMARY FOR EACH CAR-- #

# a function to get the details of a car, which are returned as a dictionary of attributes
def get_car_details(url):

    print("getting car details from: {}".format(url))

    # query the website and return the html to the variable ‘page’
    html = urllib.request.urlopen(url)

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(html, "html.parser")

    # get the data of the first <script> tag (where our data is) and convert into a string for string manipulation
    data = str(soup.find("script"))

    # cut the <script> tag and some other things from the beginning and end to get valid JSON
    cut = data[27:-13]

    # encode the data so that the json parser can handle it
    encoded = cut.encode('utf-8')

    # load the data as a json dictionary
    jsoned = json.loads(encoded)
    
    # get the subset of jsoned where the most relevant variables are
    attr_raw = jsoned["a"]["attr"]
    
    # convert all dict values in raw_attr to str if they happen to be lists (some are, some aren't), we need a homogenous set
    attr = {key: str(value[0]) for key, value in attr_raw.items() if isinstance(value, (list,))}
    
    # add prijs (from another part of jsoned) to attr
    attr["Prijs"] = int(jsoned["a"]["prc"]["amt"])/100 # divide by 100 because contains two extra zeros, make int
    # add merk (from another part of jsoned) to attr
    attr["Merk"] = jsoned["c"]["c"]["n"]
    
    # make a list of each value in attr. We need this step so the output can be read into a Pandas DataFrame later. 
    for key in attr: 
        attr[key] = [attr[key]]
    
    print("returning attr: {}".format(attr))
    
    return attr


# A function to get everything going. Takes two arguments: the base_url, the number of pages it should crawl.
def main_function(base_url, pages):

    # create the list of all urls, 
    all_urls = get_all_urls(base_url, pages)

    # create an empty dataframe we can append to
    df = pd.DataFrame()

    # go through the list of urls, for each page get the details, add them to the dataframe
    for ad_url in all_urls:
    
        # get the attr of the ad page 
        details = get_car_details(ad_url) # this fuction returns a dictionary of attr

        #append the attributes to the df
        df = df.append(details, ignore_index=True) # as we append a (possibly) different set of keys, we need to ignore the inde
        
        print("data added to df: {}".format(df))
        
        # wait a bit to not overload the server and get banned
        time.sleep(2.5)  

    # write the df to a csv file
    df.to_csv("results_marktplaats_scraper.csv", sep=";", index=False)
    
    print("results_marktplaats_scraper.csv saved to program directory")

# define base URL, the format should end with "currentpage="
base_url = "https://www.marktplaats.nl/z/auto-s/maserati.html?categoryId=128&currentPage="

# run the main function with url, pages to scrape. Use total_pages(base_url) as argument to scrape all pages
main_function(base_url, 1)
