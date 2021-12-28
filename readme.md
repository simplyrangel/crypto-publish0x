# Crypto-publish0x 
The data collection, data analysis, and data visualization scripts behind the content on the ['More Coffee More Crypto'](https://www.publish0x.com/more-coffee-more-crypto) Publish0x blog. 

['More Coffee More Crypto'](https://www.publish0x.com/more-coffee-more-crypto) documents my personal thoughts and amateur cryptocurrency market analysis. Publish0x readers -- and users in general -- are encouraged to comment and review the implemented analysis routines throughout the repository. I'm always trying to learn; constructive feedback is appreciated. 

## Dependencies
The repository's Python scripts and Jupyter Notebooks are executed in `Python3.9.7` using the `conda 4.10.3` [Anaconda environment](https://www.anaconda.com/products/individual). 

Some of the analysis scripts rely on other personal repositories. Any such external repositories are tracked in `crypto-publish0x` via git submodules. The only submodule currently tracked is the [crypto-api](https://github.com/simplyrangel/crypto-api) submodule.

## Layout
Scipts that support a given blog post are grouped in directories labeled by blog post year, month, and post number that month (indexed from zero): YYYY-MM-post-N. For example, the directory '2021-12-post-2' contains analysis scripts behind the third blog post made during Dec. 2021. 
