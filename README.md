# Web-scraping
This a web-scraping project which involves scraping specific data from yelp business search.There is a sheet which has the URLs of search results of businesses in yelp. We'll need data of 20 businesses from each of these URL. We'll skip the sponsored businesses. Each URL has 10 results per page, so we'll have to get data of 2 pages of each URL.

Images and logos will need to be direct urls hosted on a server/dropbox with links to each image in cells. I've attached the list of urls you need to scrape. The total number of links is 8811 rows. So in total 176220 businesses. 8811 x 20 is 176220.

The spreadsheet shold be formated with the following columns;Name	Address	Phone Number	Website URL	Rating	Number of reviews	Business Description	Business Hours	Business Email	Business Categories	Service Area	Business Opening Year	Business Photos(1 to 10)	Payment Method	Owner Name	Fax Number	Alternate Phone Numbers	Products and Services	Company Size	No. of reviews	Facebook Link	Twitter Link	Instagram Link	Youtube Link	Linkedin link	

# Steps
Skip Sponsored Businesses: We'll need to identify and exclude businesses that are marked as sponsored in the search results.

Pagination: Since each Yelp URL provides results across multiple pages, we'll need to ensure your scraper is capable of handling pagination to retrieve the second page of results.


Data Fields to Extract:

Business Information: Business name, address, phone number, website URL, rating, and the number of reviews.

Additional Details: Business description, hours of operation, email address, categories, service areas, opening year, payment methods, owner name, and social media links (Facebook, Twitter, Instagram, YouTube, LinkedIn).

Business Photos: You’ll need to collect up to 10 business photos and ensure the links are hosted on a server or Dropbox.

Other: Information such as fax numbers, alternate phone numbers, products and services, and company size.

Image Hosting: After scraping the business images/logos, you’ll need to download and upload them to a hosting platform like Dropbox. The hosted URLs for these images should be added to the spreadsheet.


Output Formatting: The scraped data must be formatted into a structured spreadsheet with clearly defined columns (e.g., Name, Address, Phone, Website, Ratings, Reviews, Description, Business Hours, etc.).


Scale: Since this involves scraping a large volume of data (176,220 businesses), the project must handle a high number of requests efficiently and ensure that the data is collected accurately without duplicate entries or missing fields.
