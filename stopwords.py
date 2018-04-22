# Create a stopword list using a statistical and information model
# For details in the methodology behind, see
# Zou et. al 2006, "Automatic Construction of Chinese Stop Word Lists"



import numpy as np
import pandas as pd

DICT_PATH = r'/home/csrp/csrp/code/dictionaries/'
# DICT_PATH = r'/home/lun/csrp/code/dictionaries/'

class Stopword:

#-------------------------------------------------------------------------------

    def __init__(self, series_transcript):
        # private variables
        self.__series_transcript = series_transcript
        self.__total_num_text = self.__series_transcript.count()
        self.__df_stopwords = None
        self.__df_im_stopwords = None

#-------------------------------------------------------------------------------

    # a private member function to calculate word probabilities
    def __computeWordProbabilities(self):
        df_words = []
        
        for index, list_of_tokens_in_each_text_document \
            in enumerate(self.__series_transcript.values):

            # strip tokens from model
            # find total number of instances of each word
            # and find the probabilities
            df_words.append(pd.DataFrame(list_of_tokens_in_each_text_document,
                columns=['word']) )

            numwords = df_words[index].count()[0]
            df_words[index] = df_words[index].groupby('word')['word'].count()
            df_words[index] = pd.DataFrame(df_words[index])
            df_words[index].columns = ['num_instances']
            df_words[index]['word_prob'] = \
                np.divide(df_words[index]['num_instances'], numwords)
            df_words[index]['text_num'] = index
            df_words[index].reset_index(inplace=True)

        df_words = pd.concat(df_words, axis=0, ignore_index=True)
        df_words.set_index('word', inplace=True)

        # calculate mean and variance probabilities and saturatation
        df_sumN_prob = df_words.groupby('word')['word_prob'].sum()
        df_sumN_prob.rename('sum_n_prob', inplace=True)

        df_mean_prob = np.divide(df_sumN_prob, self.__total_num_text)
        df_mean_prob.rename('mean_prob', inplace=True)

        df_sum_N_var_prob = df_words.join(pd.DataFrame(df_mean_prob) )
        df_sum_N_var_prob.reset_index(inplace=True)

        df_sum_N_var_prob['sum_N_var_prob'] = np.power(
            np.subtract(df_sum_N_var_prob['word_prob'].values,
                df_sum_N_var_prob['mean_prob'].values), 2)

        df_sum_N_var_prob = df_sum_N_var_prob.groupby(
            'word')['sum_N_var_prob'].sum()
        df_var_prob = np.divide(df_sum_N_var_prob, numwords)
        df_var_prob.rename('var_prob', inplace=True)

        self.__df_stopwords = pd.DataFrame({
            'mean_prob' : df_mean_prob,
            'var_prob' : df_var_prob,
            'sat_val' : np.divide(df_sumN_prob, df_sum_N_var_prob)
        })

        # # put this back in order
        # self.__df_stopwords = self.__df_stopwords[
        #     ['mean_prob', 'var_prob', 'sat_val']]

        # calculate entropies
        df_entropy = np.multiply(df_words['word_prob'], np.log2(
            np.reciprocal(df_words['word_prob']) ) )
        df_entropy.rename('entropy', inplace=True)
        df_entropy = pd.DataFrame(df_entropy)
        df_entropy.reset_index(inplace=True)

        self.__df_stopwords['entropy'] = \
            df_entropy.groupby('word')['entropy'].sum()

        self.__df_stopwords.sort_values('entropy', ascending=False)

#-------------------------------------------------------------------------------

    # function to generate stopword list
    # returns stopword dataframe if successful, otherwise returns None
    def generateStopwordList(self):
        self.__computeWordProbabilities()

        if self.__df_stopwords is None:
            return None

        # helper function
        # pre: attribute_type must be 'sat_val', 'mean_prob', 'var_prob', 'entropy'
        def findRank(attribute_type, bool_ascending):
            return self.__df_stopwords.sort_values(
                [attribute_type], ascending=bool_ascending ).reset_index(
                ).reset_index().set_index('word')[['index']]

        df_rank_sat_val = findRank('sat_val', True) # The higher the better
        df_rank_mean_prob = findRank('mean_prob', False)
        df_rank_var_prob = findRank('var_prob', False)
        df_rank_entropy = findRank('entropy', False)

        self.__df_im_stopwords = pd.DataFrame({
            'sat_val_rank' : df_rank_sat_val['index'],
            'mean_prob_rank' : df_rank_mean_prob['index'],
            'var_prob_rank' : df_rank_var_prob['index'],
            'entropy_rank' : df_rank_entropy['index'] })

        self.__df_im_stopwords['weight'] = self.__df_im_stopwords.sum(axis=1)
        self.__df_im_stopwords.reset_index(inplace=True)
        self.__df_im_stopwords.sort_values(
            'weight', ascending=True, inplace=True)

        return self.__df_im_stopwords

#-------------------------------------------------------------------------------

    # function to output stopword list, compatable with Jieba format
    # returns False if no stopword list generated, True if successfully generated
    def outputStopWordlist(self, num_stopwords, filename):
        if self.__df_im_stopwords is None:
            return False

        # otherwise
        self.__df_im_stopwords['index'].head(num_stopwords).to_csv(DICT_PATH + \
            filename, sep=' ', index=False, header=False)
        return True
