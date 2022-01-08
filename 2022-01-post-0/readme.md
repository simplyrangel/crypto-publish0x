# Publish0x blog post Jan. 03, 2022
Scripts in this directory support ['OlympusDAO: estimating the break-even price after one year of compounding'](https://www.publish0x.com/more-coffee-more-crypto/olympusdao-estimating-the-break-even-price-after-one-year-of-xglwvgk), published Jan. 03, 2022. 

**Thumbnail image information:**
- website: [unsplash.com](https://unsplash.com/)
- Photographer / artist: [Simone Pellegrini](https://unsplash.com/@mazerone)
- Image URL: https://unsplash.com/photos/L3QG_OBluT0

**Online resources:**
1. [OIP-18: Reward rate framework and reduction](https://forum.olympusdao.finance/d/77-oip-18-reward-rate-framework-and-reduction)
2. [OIP-63: Reward rate adjustment](https://forum.olympusdao.finance/d/755-oip-63-reward-rate-adjustment)

**Data collection steps:**
1. The Ohm supply history is used to estimate the point where the Ohm supply exceeds 10 million Ohm. Ohm supply history was manually copy-pasted from [Dune Analytics](https://dune.xyz/queries/285132) and saved as a .csv file in bin/. 

**Analysis steps:**
1. Run `estimate-break-even.py` to perform the analysis and save the relevant plots. 
