import pickle, os


PATH = os.path.expanduser('~/csrp/corpus/pickled_corpuses/')

# a class wrapper for importing HK Cantonese Corpus
class HKCantoneseCorpus:
    def __init__(self):
        self.__sentences = None

    # loads corpus without any punctuations
    def loadTokenizedSentences(self):
        os.chdir(PATH)
        with open("hkcancorpus_tokens.p", 'rb') as f:
            self.__sentences = pickle.load(f, encoding='utf-8')

        if not f.closed:
            self.__sentences = None
            return None

        return self.__sentences

#-------------------------------------------------------------------------------

    # loads tagged corpus with out any punctuations
    def loadTaggedSentences(self):
        os.chdir(PATH)
        with open("hkcancorpus_pos_tokens.p", 'rb') as f:
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
        os.chdir(PATH)
        with open("modcenturycanmoviecorpus_tokens.p", 'rb') as f:
            self.__sentences = pickle.load(f, encoding='utf-8')

        if not f.closed:
            self.__sentences = None
            return None

        return self.__sentences

#--end of MidCenturyHKCantonseMovieCoHKCantoneseCorpus Class--------------------
