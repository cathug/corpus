import pickle


PATH = '/home/csrp/csrp/code/corpus/pickled_corpuses/'

# a class wrapper for importing HK Cantonese Corpus
class HKCantoneseCorpus:
    def __init__(self):
        self.__sentences = None

    # loads corpus without any punctuations
    def loadTokenizedSentences(self):
        with open("%shkcancorpus_tokens.p" % PATH, 'rb') as f:
            self.__sentences = pickle.load(f, encoding='utf-8')

        if not f.closed:
            self.__sentences = None
            return None

        return self.__sentences

#-------------------------------------------------------------------------------

    # loads tagged corpus with out any punctuations
    def loadTaggedSentences(self):
        with open("%shkcancorpus_pos_tokens.p" % PATH, 'rb') as f:
            self.__sentences = pickle.load(f, encoding='utf-8')

        if not f.closed:
            self.__sentences = None
            return None

        return self.__sentences

#--end of HKCantoneseCorpus Class-----------------------------------------------




# a class wrapper for importing Mid Century HK Cantonese Movie Corpus
class MidCenturyHKCantoneseMovieCorpus:
    def __init__(self):
        self.__sentences = None

    # loads corpus without any punctuations
    def loadTokenizedSentences(self):
        with open("%smodcenturycanmoviecorpus_tokens.p" % PATH, 'rb') as f:
            self.__sentences = pickle.load(f, encoding='utf-8')

        if not f.closed:
            self.__sentences = None
            return None

        return self.__sentences

#--end of MidCenturyHKCantonseMovieCoHKCantoneseCorpus Class--------------------
