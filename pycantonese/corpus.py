# -*- coding: utf-8 -*-

# PyCantonese
#
# Copyright (C) 2014-2017 PyCantonese Project
# Author: Jackson Lee <jacksonlunlee@gmail.com>
# URL: <http://pycantonese.org/>
# For license information, see LICENSE.TXT


# Note: This file has been modified on January 31, 2018 
# It has two added methods in the class CantoneseCHATReader
# which will allow easier parsing of data stored in CHAT files


import os

from pylangacq.chat import Reader

from pycantonese.search import perform_search
from pycantonese.util import ENCODING, get_jyutping_from_mor, ListFromIterables


class CantoneseCHATReader(Reader):
    """A class for reading Cantonese CHAT corpus files."""
    def __init__(self, *filenames, **kwargs):
        encoding = kwargs.get('encoding', ENCODING)
        super(CantoneseCHATReader, self).__init__(*filenames,
                                                  encoding=encoding)

    def concordance(self, search_item, participant=None, exclude=None,
                    match_entire_word=True, lemma=False, by_files=False):
        raise NotImplementedError('coming soon!')

    def _get_jyutping_sents(self, participant=None, exclude=None, sents=True):
        fname_to_tagged_sents = self.tagged_sents(participant=participant,
                                                  exclude=exclude,
                                                  by_files=True)

        fn_to_jyutpings = {}
        jyutpings_list = []

        for fn in self.filenames():
            fn_to_jyutpings[fn] = []
            tagged_sents = fname_to_tagged_sents[fn]

            for tagged_sent in tagged_sents:
                if sents:
                    jyutpings_list = []

                for tagged_word in tagged_sent:
                    _, _, mor, _ = tagged_word
                    jyutping = get_jyutping_from_mor(mor)

                    if sents:
                        jyutpings_list.append(jyutping)
                    else:
                        fn_to_jyutpings[fn].append(jyutping)

                if sents:
                    fn_to_jyutpings[fn].append(jyutpings_list)

        return fn_to_jyutpings




    def jyutpings(self, participant=None, exclude=None, by_files=False):
        """
        Return a list of jyutping strings by *participant* in all files.

        :param participant: Specify the participant(s); defaults to all
            participants.

        :param by_files: If True (default: False), return dict(absolute-path
            filename: X for that file) instead of X for all files altogether.

        :rtype: list(str), or dict(str: list(str))
        """
        fn_to_jyutpings = self._get_jyutping_sents(participant=participant,
                                                   exclude=exclude,
                                                   sents=False)

        if by_files:
            return fn_to_jyutpings
        else:
            return ListFromIterables(*(v for _, v in
                                       sorted(fn_to_jyutpings.items())))

    def jyutping_sents(self, participant=None, exclude=None, by_files=False):
        """
        Return a list of sents of jyutping strings
        by *participant* in all files.

        :param participant: Specify the participant(s); defaults to all
            participants.

        :param by_files: If True (default: False), return dict(absolute-path
            filename: X for that file) instead of X for all files altogether.

        :rtype: list(list(str)), or dict(str: list(list(str)))
        """
        fn_to_jyutpings = self._get_jyutping_sents(participant=participant,
                                                   exclude=exclude,
                                                   sents=True)

        if by_files:
            return fn_to_jyutpings
        else:
            return ListFromIterables(*(v for _, v in
                                       sorted(fn_to_jyutpings.items())))

    def _get_character_sents(self, participant=None, exclude=None, sents=True):
        fname_to_tagged_sents = self.tagged_sents(participant=participant,
                                                  exclude=exclude,
                                                  by_files=True)

        fn_to_characters = {}
        characters_list = []

        for fn in self.filenames():
            fn_to_characters[fn] = []
            tagged_sents = fname_to_tagged_sents[fn]

            for tagged_sent in tagged_sents:
                if sents:
                    characters_list = []

                for tagged_word in tagged_sent:
                    chs, _, _, _ = tagged_word

                    if chs and '\u4e00' <= chs[0] <= '\u9fff':
                        characters_in_word = list(chs)
                    else:
                        characters_in_word = [chs]

                    if sents:
                        characters_list.extend(characters_in_word)
                    else:
                        fn_to_characters[fn].extend(characters_in_word)

                if sents:
                    fn_to_characters[fn].append(characters_list)

        return fn_to_characters
        
        
    # extra method to get segmented words in the transcript
    def _get_word_sents(self, participant=None, exclude=None, sents=True):
        fname_to_tagged_sents = self.tagged_sents(participant=participant,
                                                  exclude=exclude,
                                                  by_files=True)

        fn_to_words = {}
        word_list = []

        for fn in self.filenames():
            fn_to_words[fn] = []
            tagged_sents = fname_to_tagged_sents[fn]

            for tagged_sent in tagged_sents:
                if sents:
                    word_list = []

                for tagged_word in tagged_sent:
                    chs, _, _, _ = tagged_word

                    characters_in_word = [chs]

                    if sents:
                        word_list.extend(characters_in_word)
                    else:
                        fn_to_words[fn].extend(characters_in_word)

                if sents:
                    fn_to_words[fn].append(word_list)

        return fn_to_words
        
        
        
    
    # extra method to get part of speech in the transcript
    def _get_pos_sents(self, participant=None, exclude=None, sents=True):
        fname_to_tagged_sents = self.tagged_sents(participant=participant,
                                                  exclude=exclude,
                                                  by_files=True)

        fn_to_pos = {}
        pos_list = []

        for fn in self.filenames():
            fn_to_pos[fn] = []
            tagged_sents = fname_to_tagged_sents[fn]

            for tagged_sent in tagged_sents:
                if sents:
                    pos_list = []

                for tagged_pos in tagged_sent:
                    _, pos_tag, _, _ = tagged_pos

                    pos_of_word = [pos_tag]

                    if sents:
                        pos_list.extend(pos_of_word)
                    else:
                        fn_to_pos[fn].extend(pos_of_word)

                if sents:
                    fn_to_pos[fn].append(pos_list)

        return fn_to_pos
        
    
    

    def characters(self, participant=None, exclude=None, by_files=False):
        """
        Return a list of Chinese characters by *participant* in all files.

        :param participant: Specify the participant(s); defaults to all
            participants.

        :param by_files: If True (default: False), return dict(absolute-path
            filename: X for that file) instead of X for all files altogether.

        :rtype: list(str), or dict(str: list(str))
        """
        fn_to_characters = self._get_character_sents(participant=participant,
                                                     exclude=exclude,
                                                     sents=False)

        if by_files:
            return fn_to_characters
        else:
            return ListFromIterables(*(v for _, v in
                                       sorted(fn_to_characters.items())))

    def character_sents(self, participant=None, exclude=None, by_files=False):
        """
        Return a list of sents of Chinese characters
        by *participant* in all files.

        :param participant: Specify the participant(s); defaults to all
            participants.

        :param by_files: If True (default: False), return dict(absolute-path
            filename: X for that file) instead of X for all files altogether.

        :rtype: list(list(str)), or dict(str: list(list(str)))
        """
        fn_to_characters = self._get_character_sents(participant=participant,
                                                     exclude=exclude,
                                                     sents=True)

        if by_files:
            return fn_to_characters
        else:
            return ListFromIterables(*(v for _, v in
                                       sorted(fn_to_characters.items())))
                                       
                                       
    # Two extra functions added 
    def word_sents(self, participant=None, exclude=None, by_files=False):
        """
        Return a list of sents of Chinese words
        by *participant* in all files.

        :param participant: Specify the participant(s); defaults to all
            participants.

        :param by_files: If True (default: False), return dict(absolute-path
            filename: X for that file) instead of X for all files altogether.

        :rtype: list(list(str)), or dict(str: list(list(str)))
        """
        fn_to_words = self._get_word_sents(participant=participant,
                                           exclude=exclude,
                                           sents=True)

        if by_files:
            return fn_to_words
        else:
            return ListFromIterables(*(v for _, v in
                                       sorted(fn_to_words.items())))
                                       
    
    
    def pos_sents(self, participant=None, exclude=None, by_files=False):
        """
        Return a list of sents of Chinese words
        by *participant* in all files.

        :param participant: Specify the participant(s); defaults to all
            participants.

        :param by_files: If True (default: False), return dict(absolute-path
            filename: X for that file) instead of X for all files altogether.

        :rtype: list(list(str)), or dict(str: list(list(str)))
        """
        fn_to_pos = self._get_pos_sents(participant=participant,
                                        exclude=exclude,
                                        sents=True)

        if by_files:
            return fn_to_pos
        else:
            return ListFromIterables(*(v for _, v in
                                       sorted(fn_to_pos.items())))                                   
                                       
                                       
    

    def search(self, onset=None, nucleus=None, coda=None, tone=None,
               initial=None, final=None, jyutping=None,
               character=None, pos=None,
               word_range=(0, 0), sent_range=(0, 0),
               tagged=True, sents=False,
               participant=None, exclude=None, by_files=False):
        """
        Search for the specified element(s).

        **Jyutping elements**

        Parameters are *onset*, *nucleus*, *coda*, *tone*, *initial*,
        *final*, *jyutping*.
        If *jyutping* is used, none of the other Jyutping elements can be.
        If *final* is used, neither *nucleus* nor *coda* can be.
        *onset* and *initial* cannot conflict, unless one or both of them are
        None.
        Regular expression matching applies to
        *onset*, *nucleus*, *coda*, *tone*, and *initial*.

        **Chinese character**

        Parameter: *character* (only one is allowed)

        **Part-of-speech tag**

        Parameter: *pos*

        Regular expression matching applies.

        **Word or sentence range**

        *word_range*: specify the span of words to the left and right
        of a match word; defaults to ``(0, 0)``.

        *sent_range*: specify the span of sents preceding and following
        the sent containing a match word; defaults to ``(0, 0)``.

        If *sent_range* is used, *word_range* is ignored.

        **Output formatting**

        If *sents* is True (the default), sents containing a match word are
        returned; otherwise just a word instead.

        If *tagged* is True (the default), words are tagged in the form of
        (word, pos, jyutping, rel); otherwise just word token strings.

        *by_files*: If False (the default), the return object is a list
        encompassing search results for all files. If True, the return object
        is dict(absolute-path filename: list of search results for that file)
        instead.

        **Others**

        *participant*: specify the participant(s) (default: all participants).
        """
        fn_to_results = perform_search(
            self.tagged_sents(participant=participant,
                              exclude=exclude, by_files=True),
            onset=onset, nucleus=nucleus, coda=coda, tone=tone,
            initial=initial, final=final, jyutping=jyutping,
            character=character, pos=pos,
            word_range=word_range, sent_range=sent_range,
            tagged=tagged, sents=sents)

        if by_files:
            return fn_to_results
        else:
            return ListFromIterables(*(v for _, v in
                                       sorted(fn_to_results.items())))


def hkcancor():
    """
    Create the corpus object for the Hong Kong Cantonese Corpus.
    """
    data_path = os.path.join(os.path.dirname(__file__),
                             'data', 'hkcancor', '*.cha')
    return CantoneseCHATReader(data_path, encoding='utf8')


def read_chat(*filenames, **kwargs):
    """
    Create a corpus object based on *filenames*.

    :param filenames: one or multiple filenames (absolute-path or relative to
        the current directory; with or without glob matching patterns)

    :param kwargs: Keyword arguments. Currently, only ``encoding`` is
        recognized, which defaults to 'utf8'.
    """
    encoding = kwargs.get('encoding', ENCODING)
    return CantoneseCHATReader(*filenames, encoding=encoding)
