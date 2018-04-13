# code to automate tokenization with online LIVAC tokenizer
# TODO: add postgre and sqlalchemy code

import re, csv, pickle, time, sys, textwrap
from itertools import cycle

import requests
from requests import Session
# from requests.utils import dict_from_cookiejar
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from pprint import pprint
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd

# postgre database binders
import psycopg2


# global variables
URL = 'http://www.livac.org/seg/livac_seg_index.php'
# CSV_PATH = r'/home/lun/Desktop/'
PICKLE_PATH = '/home/csrp/csrp/code/corpus/pickle/'

PROXIES = {
  'http': 'http://113.254.44.242:80',
  'http': 'http://47.90.87.225:88',
  'http': 'http://45.115.39.139:7777'
}

PROXY = next(cycle(PROXIES))

#-------------------------------------------------------------------------------

def printUsage():
    print(textwrap.dedent(
        '''
            Extraction Instructions:
            ------------------------
            1. Enable Python Virtual Environment
            2. Run the script:
                    $ python livac.py PICKLE_FILE_NUM TIME_DELAY IS_RESUME
               where:
                    PICKLE_FILE_NUM     the pickle file number X, i.e.
                                            pickled_wiki_entries_X.p
                    TIME_DELAY          the number of delayed seconds
                                            between scrapes (int)
                    IS_RESUME           whether to resume from unfinished
                                            scrape. 0 for false, 1 for true.
        '''
    ))

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

    # pr = requests_retry_session(
    #     retries=10, session=session).post(URL, data=form_data)
    pr = session.post(URL, data=form_data)#, proxies={"http": PROXY, "https": PROXY})
    if pr.status_code == requests.codes.ok: # returns a 200 OK
        print("POST Response ok")
        return pr
    else:
        raise requests.ConnectionError(
            'POST Response returns a status code %d.' % pr.status_code )
        return None

#-------------------------------------------------------------------------------

# Function to parse input text and output tokens from an HTML response
# precondition: html_body must be from LIVAC POST response
# parameters:   html_body - the LIVAC HTML payload excluding header information
# returns:      the original text input and tokenized output
def parseTokenizedText(html_body):
    # html5lib parser keeps English in place, unlike html.parser
    # which removes them
    if html_body is None:
        raise ParsingError('Empty HTML body.')
        return

    bs = BeautifulSoup(html_body, "html5lib")
    if '使用次數已達上限' in str(bs.find('div', class_='header')):
        raise ParsingError('Current IP has exceeded daily limit')
        return

    # otherwise
    original_text = bs.find("textarea", id="search")
    tokens = bs.find("textarea", id="segmentResult")
    if tokens is None: # can't find token string
        raise ParsingError('Cannot find token string in HTML response.')
        return

    # return original_text.text, re.sub(r'[\<\>]', '', tokens.text)
    return re.sub(r'[\<\>]', '', tokens.text) # otherwise

#-------------------------------------------------------------------------------

# this function came from
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# Repeats binary backoff when the server returns a 500, 502 or 504,
# then terminates when the number of retries has been depleted
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

# # Function to output parsed strings to a CSV file
# # parameters:   file_name - intended file name
# #               header_names - given header names
# #               parsed_list - an ordered dictionary of elements
# # returns:      the original text input and tokenized output
# def outputCSV(file_name, header_names, parsed_list):
#     with open(CSV_PATH + file_name, 'a', encoding='utf-8') as f:
#         writer = csv.writer(f)
#
#         # first write a header
#         writer.writerow(header_names)
#
#         # write row by row
#         for original_text, tokens in parsed_list:
#             writer.writerow([original_text, tokens])
#
#     assert(f.closed)

#-------------------------------------------------------------------------------

# function to pickle dataframe
def pickleDataframe(dataframe, filename):
    with open(filename, 'wb') as f:
        pickle.dump(dataframe, f)
    if f.closed:
        return True
    return False # otherwise

#-------------------------------------------------------------------------------

# function to depickle dataframe
def depickleDataframe(filename):
    with open(filename, 'rb') as f:
        dataframe = pickle.load(f, encoding='utf-8')
    if f.closed:
        return dataframe
    return False

#-------------------------------------------------------------------------------

def readTableIndexLog():
    with open('index.log', 'r') as f:
        pos = f.read()
    if f.closed:
        return int(pos)
    return None

#-------------------------------------------------------------------------------

def writeTableIndexLog(position):
    with open('index.log', 'w') as f:
        f.write(str(position) )
    if f.closed:
        return True
    return False

#-------------------------------------------------------------------------------
# Error Classes
class ParsingError(Exception):
    pass

#-------------------------------------------------------------------------------

# database
class Database(object):
    def __init__(self, *,
                 db_name, db_user, user_password,
                 host, port):
        super([object Object], self).__init__()
        self.__conn = psycopg2.connect(
            databse=db_name,
            user=db_user,
            password=user_password,
            host=host,
            port=port
        )
        self.__cur = None

        if self.__conn:
            self.__cur = self.__conn.cursor()

    def createTable(self, *, tablename, schema):
        # create table
        if self.__cur and self.__conn: # if created successfully
            self.__cur.execute("CREATE TABLE %s (% s);" % (tablename, schema ) )

    def deleteEntryInTable(self, *, tablename, schema):
        if self.__cur and self.__conn:
            self.__cur.execute("DELETE from %s where %s;" % (tablename, schema ) )
            self.__conn.commit

    def updateEntryInTable(self, *, tablename, schema):
        if self.__cur and self.__.conn:
            self.__cur.execute("UPDATE %s set %where " % (tablename, schema ) )

    def closeDatabase(self):
        self.__cur.close()
        self.__conn.close()





# main function
def main():
    # Perform argument checks
    if len(sys.argv) != 4:
        printUsage()
        sys.exit("Error: Invalid number of arguments.  Four required")


    # check if arguments are sound
    # if yes, cast constants as integers,
    # otherwise
    SYS_PICKLE_FILE_NUM = sys.argv[1]
    SYS_TIME_DELAY = sys.argv[2]
    SYS_IS_RESUME = sys.argv[3]

    if not SYS_PICKLE_FILE_NUM.isdigit() or \
        not SYS_TIME_DELAY.isdigit() or \
        not SYS_IS_RESUME.isdigit():
        printUsage()
        sys.exit("Error: At least one argument is not an integer")

    SYS_PICKLE_FILE_NUM = int(SYS_PICKLE_FILE_NUM)
    SYS_TIME_DELAY = int(SYS_TIME_DELAY)
    SYS_IS_RESUME = int(SYS_IS_RESUME)


    # depickle proper wiki dump
    if SYS_IS_RESUME == 0:
        try:
            df_wiki = depickleDataframe(
                PICKLE_PATH + "pickled_wiki_entries_%s.p" % SYS_PICKLE_FILE_NUM)
        except FileNotFoundError:
            sys.exit("Invalid pickle file")
        startpos = 0 # if try is successful
    elif SYS_IS_RESUME == 1:
        try:
            df_wiki = depickleDataframe("backup.p")
        except FileNotFoundError:
            sys.exit("Backup pickle file does not exist.")
        startpos = readTableIndexLog()
        # print(startpos)
    else:
        printUsage()
        sys.exit("Error: Invalid argument in Pos 4.  Only 1 or 0 accepted.")

    # print(startpos)
    # return


    # init session
    lang = 'tc' # Traditional Chinese
    payload = {'lang' : lang}
    s = requests_retry_session()
    # s = requests.Session()
    if s is None:
        sys.exit("Request session terminates prematurely.")

    gr = s.get(URL, params=payload)#, proxies={"http": PROXY, "https": PROXY})
    if gr == None:
        s.close()
        sys.exit("Init GET request failed.")
    # print(s.url)
    # print(s.encoding)
    # print(s.status_code)
    if gr.status_code != requests.codes.ok: # not returning a 200 OK
        s.close()   # close the TCP session
        sys.exit("GET Request returns status code: %d" % gr.status_code)
    print("GET Request ok") # otherwise

    # Do this n times
    # get response from POST
    for i, text in enumerate(df_wiki['text'].tolist(), startpos ):
        print('Scraping entry #%d\n' %i)
        text_length = len(text)

        # Text length must be capped under 1000 characters.
        # if too long or too short, do not send to server and move to next entry
        if text_length < 10 and text_length > 1000:
            print(
                "Invalid input string. " + \
                "Must be between 10 and 1000 characters. " + \
                "Proceeding to next string input.\n"
            )

        else:
            try: # send POST request and get response back
                response = postUnsegmentedString(s, text, lang)

            # handle all errors, including socket errors and Ctrl+C termination
            except: #(requests.RequestException, KeyboardInterrupt, requests.ConnectionError):
                if i > 0:
                    pickleDataframe(df_wiki, 'backup.p')
                    writeTableIndexLog(i)
                s.close() # all cases including i <= 0
                sys.exit("Connection closed prematurely.")

            # if try clause is successful
            # PHPSESSID = dict_from_cookiejar(s.cookies)['PHPSESSID'] # get PHPSESSID
            # print(PHPSESSID)
            try:
                ptt_response = parseTokenizedText(response.text)
            except:
                pickleDataframe(df_wiki, 'backup.p')
                writeTableIndexLog(i)
                s.close()
                sys.exit("IP has exceeded daily limit.")

            # otherwise save to dataframe
            df_wiki.loc[df_wiki.index == i, 'tokens'] = ptt_response

            print("delaying for %d seconds\n" % SYS_TIME_DELAY)
            time.sleep(SYS_TIME_DELAY) # to not crash server, delay next request
            print("------------------------")


    # # create a list to save all processed text
    # # output results to a csv file
    # csv_header = ["original_text", "tokens"]
    # outputCSV("tokens.txt", csv_header, parsed_strings)

    pickleDataframe(df_wiki,
        "updated_pickled_wiki_entries_%s.p" % SYS_PICKLE_FILE_NUM)

    s.close() # close the TCP connection
    sys.exit(0)

if __name__ == '__main__':
    main()
