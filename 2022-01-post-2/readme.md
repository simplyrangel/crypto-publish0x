# Publish0x blog post Jan. 15, 2022

Scripts in this directory support ["Algorand governance period 2 vs 1: more rewards, fewer governors, and mysterious whales"](https://www.publish0x.com/more-coffee-more-crypto/algorand-governance-period-2-vs-1-more-rewards-fewer-governo-xglrywm) published Jan. 15, 2022.

**Thumbnail image information:**
- Website: [unsplash.com](https://unsplash.com/)
- Photographer / artist: [Kanchanara](https://unsplash.com/@kanchanara)
- Image URL: https://unsplash.com/photos/ow-rGjlqJkM

**Online resources:**
- [Algorand Foundation's governance API](https://governance.algorand.foundation/api/documentation/)

**Analysis steps:**
1. Run `query-governance-api.py` to download governor data for governance period 1 and governance period 2. The data are saved to `bin/YYYY-MM-DD-algorand-governance-period-PERIOD.hdf`, where YYYY-MM-DD is the day `query-governance-api.py` is executed, and PERIOD is the governance period. 
2. Run `plot-governance.py` to extract information from the governance data queried in step 1, and generate plots. 
