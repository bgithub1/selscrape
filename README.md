### selscrape - simple webscraping wrapper around python selenium (currently supports +3.5)
The selscrape project contains the following classes:
1. SelScrape - a class that simplifies calls to selenium to:
  * navigate to website urls
  * extract information from website elements using xpath
  * enter information on forms of a website using xpath
  * click on buttons, etc
  * simplify downloading files from urls

2. SelDictAccess - a simpler form of SelScrape that allows you to pass a dictionary of xpath statements to use when accessing html elements.
3. CraigAccess - access auto information from Craigslist using SelScrape and SelDictAccess.
4. ChaseCareers - another example of using SelScrape to extract job postings from the jpmorganchase careers website.

#### See the examples.ipynb jupyter notebook for some simple examples of this project.

