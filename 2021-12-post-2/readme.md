# Publish0x blog post Dec. 26, 2021
Scripts in this directory support ['Predicting bullish behavior with marketcap rank changes (PART-3)'](https://www.publish0x.com/more-coffee-more-crypto/predicting-bullish-behavior-with-marketcap-rank-changes-part-xznjlwe), published Dec. 26, 2021. 

Thumbnail image information:
- website: [unsplash.com](https://unsplash.com/)
- Photographer / artist: [Executium](https://unsplash.com/@executium)
- Image URL: https://unsplash.com/photos/rayxJJNKyhc

Data collection steps:
1. Manually download daily price data for each coin in `coins-of-interest.xlsx` from [coingecko.com](https://www.coingecko.com/en) and save to bin/. A webscraper to download this data automatically would be more elegant, but I couldn't figure out how to write one for coingecko.com in a timely fashion. 
2. Run `scrape-cmc.py` to scrape historical weekly coin market cap rankings from [coinmarketcap.com](https://coinmarketcap.com/historical/). `scrape-cmc.py` saves the results in a multiindex pandas dataframe named `bin/cmc-scrape-results*.hdf`. 

Analysis steps:
1. Run `data-setup.py` to format `bin/cmc-scrape-results*.hdf` and extract meaningful data from it. 
2. Run `data-explorer.py`, `price-vs-rolling-means.py`, and `price-and-market-rank-change.py` to generate plots and various datasets of interest. Various parameters within these three scripts can be tweaked to expand the analysis scope. 
