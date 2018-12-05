# Marktplaats_scraper

This is a scraper written in Python. It uses BeautifulSoup, a Python library for pulling data out of HTML and XML files, and Pandas for data storage and manipulation. It is designed to scrape data from the largest Dutch second hand market, Marktplaats.nl.

The scraper can do the following:

1. Browse through all the pages of a listing on Marktplaats.nl
2. Make a list of all the links to the individual  ads
3. Visit each ad page scrape the details (brand, model, price, etc.)
4. Add all the details to a results table (one line per ad) and save as a .CSV document

The current implementation of this scraper is "cars", but the fields scraped in step 3 can be adjusted to scrape any type of ad. 

You are free to use this code as you like, but please be aware that using this code probably violates Marktplaats.nl terms. 
So use this at your own risk, and make sure to be a smart and responsible user (i.e. don't scrape tons of pages that create a huge server load, you will probably get banned).
