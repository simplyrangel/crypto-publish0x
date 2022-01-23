# Publish0x blog post Jan. 18, 2022

Scripts in this directory support ["Large Cap Crypto portfolio update: down, but not out"](https://www.publish0x.com/more-coffee-more-crypto/large-cap-crypto-portfolio-update-down-but-not-out-xjogmxr) published Jan. 18, 2022.

**Thumbnail image information:**
- Website: [unsplash.com](https://unsplash.com/)
- Photographer / artist: [Michael Fortsch](https://unsplash.com/@michael_f)
- Image URL: https://unsplash.com/photos/gRAS87wSVCs

**Analysis steps:**
1. Make sure the [crypto-api](https://github.com/simplyrangel/crypto-api/tree/4af71a79729e3493d4961b60a4813b532ef58dab) submodule is at commit 4af71a7. 
2. Save KuCoin and Coinbase Pro account API keys as `.secret` files in bin/. 
3. Run `lcc-portfolio-data.py` to collect KuCoin and Coinbase Pro portfolio data. 
4. Run `extract-performance-metrics.py` to extract verious performance metrics from the data queried from KuCoin and Coinbase Pro in `lcc-portfolio-data.py`.
5. Run `calculate-btc-baseline.py` to generate a baseline dollar-cost-average portfolio's history. 
6. Run `plot-performance.py` to generate plots. 
