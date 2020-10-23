# corpus

last updated: Oct 23, 2020
---

## PIP requirements
+ `PyCantonese`
+ `Beautiful Soup`
+ `Requests`
+ `Pandas`, `numpy`, `jupyter` and related libraries

## Highlights
This repository contains a few tools for doing Cantonese NLP from scratch:
+ PyCantonese/HKCanCor Spoken Cantonese Corpus (pickle and raw `CHAT` files)
+ Baptist U 20th Century Black and White Movie Spoken Cantonese Corpus (pickle and raw tokenized `csv` files)
+ `hkcancorpus.ipynb`: Code for processing PyCantonese Corpus and compile dictionaries (tokens and POS tags) and HMM training data (BMES tagging and POS tagging) for `Jieba` Tokenizer 
+ `stopwords.py`: Stopword List Generator based on Zou et. al 2006, "Automatic Construction of Chinese Stop Word Lists": implemented in `pandas` and `hkcancorpus.ipynb` for usage.
+ `kwong chow cantonese dictionary.ipynb`: cleaning code for Kwong Chow Cantonese Dictionary downloaded from the web 
+ `wiki dump preprocessing.ipynb` Cantonese Wiki dump preprocessing code
+ `livac.py` - File to send text to online LIVAC tokenizer and save results in locally.  Server limits requests to 1000 per day.