# Publish0x blog post Jan. 09, 2022

Scripts in this directory support ["OlympusDAO: the key to your Ohm profits starts with this break-even curve"](https://www.publish0x.com/more-coffee-more-crypto/olympusdao-the-key-to-your-ohm-profits-starts-with-this-brea-xelxpjd) published Jan. 09, 2022.

**Thumbnail image information:**
- Website: [unsplash.com](https://unsplash.com/)
- Photographer / artist: [Clark Van Der Beken](https://unsplash.com/@snapsbyclark?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)
- Image URL: https://unsplash.com/photos/jMtN2ACBsQw

**Online resources:**
- [OIP-63: Reward rate adjustment](https://forum.olympusdao.finance/d/755-oip-63-reward-rate-adjustment)
- [Reddit post 2022-01-03: OIP-63 is beginning](https://www.reddit.com/r/olympusdao/comments/rv0p88/oip63_beginning/)
- [OlympusDAO emissions predictions on Dune Analytics](https://dune.xyz/pottedmeat/Emissions-Predictions)

**Analysis steps:**
1. Run `generate-dispersions.py` to generate and plot rebase rewards rate dispersions based on OIP-63. The dispersions are saved to `bin/rebase-rate-estimates.csv`. 
2. Run `ohm-accrual.py` to model the Ohm accrued throughout 2022 using `bin/rebase-rate-estimates.csv`. The break-even price at each rebase event is calculated based on a 1-Ohm purchased 2022-01-09. 
