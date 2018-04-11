# code to automate tokenization with online LIVAC tokenizer

import requests, re, csv, pickle, time
from requests import Session
from requests.utils import dict_from_cookiejar
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pprint import pprint
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

# global variables
URL = 'http://www.livac.org/seg/livac_seg_index.php'
# CSV_PATH = r'/home/lun/Desktop/'

#-------------------------------------------------------------------------------

# Function to post unsegmented strings
# precondition: lang must be either 'tc', or 'sc'
#               length of unseg_text must be <= 1000
# parameters:   cookie - PHPSESSID cookie
#               unseg_string - unsegmented string.
#                   Can be a combo of Chinese and English
#               lang - tc for Traditional Chinese,
#                   or sc for Simplified Chinese
# returns:      the post message, including headers and body
def postUnsegmentedString(session, unseg_string, lang):
    # fill all whitespaces with '+'
    # This is how LIVAC deals with whitespaces
    unseg_string = re.sub(
        r"\s+", r"+", unseg_string, re.DOTALL|re.MULTILINE)

    form_data = {
        'action' : 'search',
        'lang' : lang,
        'search' : unseg_string
    }

    pr = requests_retry_session(
        retries=10, session=session).post(URL, data=form_data)
    if pr.status_code == requests.codes.ok: # returns a 200 OK
        print("POST Response ok")
        return pr
    else:
        print("POST Response returns status code %d" % pr.status_code)
        return None

#-------------------------------------------------------------------------------

# Function to parse input text and output tokens from an HTML response
# precondition: html_body must be from LIVAC POST response
# parameters:   html_body - the LIVAC HTML payload excluding header information
# returns:      the original text input and tokenized output
def parseTokenizedText(html_body):
    # html5lib parser keeps English in place, unlike html.parser
    # which removes them
    bs = BeautifulSoup(html_body, "html5lib")
    original_text = bs.find("textarea", id="search")
    tokens = bs.find("textarea", id="segmentResult")
    # return original_text.text, re.sub(r'[\<\>]', '', tokens.text)
    return re.sub(r'[\<\>]', '', tokens.text)

#-------------------------------------------------------------------------------

# this function came from
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# Repeats binary backoff when the server returns a 500, 502 or 504, and stops
# when the number of retries have depleted
# According to RFC the cap for the number of tries is 16
def requests_retry_session(retries=8,
                           backoff_factor=0.3,
                           status_forcelist=(500, 502, 504),
                           session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

#-------------------------------------------------------------------------------

# Function to output parsed strings to a CSV file
# parameters:   file_name - intended file name
#               header_names - given header names
#               parsed_list - an ordered dictionary of elements
# returns:      the original text input and tokenized output
def outputCSV(file_name, header_names, parsed_list):
    with open(CSV_PATH + file_name, 'a', encoding='utf-8') as f:
        writer = csv.writer(f)

        # first write a header
        writer.writerow(header_names)

        # write row by row
        for original_text, tokens in parsed_list:
            writer.writerow([original_text, tokens])

    assert(f.closed)

#-------------------------------------------------------------------------------

def pickleDataframe(dataframe, filename):
    with open(filename, 'wb') as f:
        pickle.dump(dataframe, f)
    if f.closed:
        return True
    return False # otherwise

#-------------------------------------------------------------------------------

def depickleDataframe(filename):
    with open(filename, 'rb') as f:
        dataframe = pickle.load(f, encoding='utf-8')
    if f.closed
        return dataframe
    return False

#-------------------------------------------------------------------------------

# main function
def main():
    # depickle wiki dump
    df_wiki = depickleDataframe("/home/lun/csrp/code/early_warning_system/pickled_wiki_entries.p")

    # Traditional Chinese
    lang = 'tc'

    # init session
    payload = {'lang' : lang}
    gr = requests_retry_session().get(URL, params=payload)
    if gr == None:
        print("Session failed")
        return

    # print(s.url)
    # print(s.encoding)
    # print(s.status_code)
    if gr.status_code != requests.codes.ok: # not returning a 200 OK
        print("GET Request returns status code: %d" % gr.status_code)
        s.close()   # close the TCP session
        return

    # otherwise
    print("GET Request ok")


    # Do this n times
    # get response from POST
    for i, text in enumerate(df_wiki['text'].tolist() ):
        text_length = len(text)

        if text_length < 2:
            print("Input string too short\n")

        elif text_length > 1000:
            print("Input string too long.  Must be 1000 characters or less.\n")

        else:
            response = postUnsegmentedString(s, text, lang)
            PHPSESSID = dict_from_cookiejar(s.cookies)['PHPSESSID'] # get PHPSESSID
            # print(PHPSESSID)
            if not response:
                s.close()
                return

            df_wiki.loc[df_wiki.index == i, 'tokens'] = \
                parseTokenizedText(response.text)
            print("delaying for 5 seconds")
            time.sleep(5) # to not crash server, delay next request for 5 seconds


    # # create a list to save all processed text
    # # output results to a csv file
    # csv_header = ["original_text", "tokens"]
    # outputCSV("tokens.txt", csv_header, parsed_strings)

    pickleDataframe(df_wiki, "updated_pickled_wiki_entries.p")

    s.close() # close the TCP connection
    return 0

if __name__ == '__main__':
    main()
