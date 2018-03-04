# code to automate tokenization with online LIVAC tokenizer

import requests, re, csv
from requests import Session
from requests.utils import dict_from_cookiejar
from pprint import pprint
from bs4 import BeautifulSoup

# global variables
URL = 'http://www.livac.org/seg/livac_seg_index.php'
CSV_PATH = r'/home/lun/Desktop/'


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

    pr = session.post(URL, data=form_data)
    if pr.status_code == requests.codes.ok: # returns a 200 OK
        print("POST Response ok")
        return pr
    else:
        print("POST Response returns status code %d" % pr.status_code)
        return None



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
    return original_text.text, re.sub(r'[\<\>]', '', tokens.text)



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



# main function
def main():
    text_list = [
        "全國政協在北京舉行小組會議，審議政協常委會工作報告。",
        "今年全國人大會議由周一起至本月20日閉幕，特首林鄭月娥會列席。"
    ]

    lang = 'tc'

    # init session
    s = requests.Session()
    payload = {'lang' : lang}
    gr = s.get(URL, params=payload)
    # print(s.url)
    # print(s.encoding)
    # print(s.status_code)
    if gr.status_code != requests.codes.ok: # not returning a 200 OK
        print("GET Request returns status code: %d" % gr.status_code)
        s.close()   # close the TCP session
        return

    # otherwise
    print("GET Request ok")

    # cookies = {'livacuser' : 'guest'}


    # Do this n times
    # get response from POST
    parsed_strings = []
    for text in text_list:
        if len(text) > 1000:
            "Input string too long.  Must be 1000 characters or less."
            return

        response = postUnsegmentedString(s, text, lang)
        PHPSESSID = dict_from_cookiejar(s.cookies)['PHPSESSID'] # get PHPSESSID
        print(PHPSESSID)
        if not response:
            s.close()
            return

        parsed_strings.append(parseTokenizedText(response.text))


    # create a list to save all processed text
    # output results to a csv file
    csv_header = ["original_text", "tokens"]
    outputCSV("tokens.txt", csv_header, parsed_strings)


if __name__ == '__main__':
    main()
