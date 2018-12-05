# Marktplaats_scraper

This is scraper written in Python. It uses BeautifulSoup, a Python library for pulling data out of HTML and XML files, and Pandas for data storage and manipulation.

The scraper is built to do the following:

1. Browse through all the pages of a listing (its current implementation: cars) on Marktplaats.nl
2. Make a list of all URLs to the individual car ads
3. Visit each car ad scrape the details of the car (brand, model, price, etc.)
4. Add all the car details to a results table (one line per car) and save as a .CSV document

The current implementation of this scraper is "cars", but the fields scraped in step 3 can be adjusted to scrape any type of ad. 

You are free to use this code as you like, but please be aware that using the code probably violates Marktplaats.nl terms. 
So use this at your own risk, and make sure to be a smart and responsible user (i.e. don't scrape tons of pages that create a huge server load, you will probably get banned).
