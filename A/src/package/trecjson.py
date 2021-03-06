import re
import nltk

epsilon = 1e-30

class TrecJson:
    def __init__(self, stopword_set):
        self.stopword_set = stopword_set

    # term level
    def is_rt(self, term):
        return term == 'RT'

    def is_url(self, term):
        return r'http://' in term or r'https://' in term

    def is_at_user(self, term):
        return len(term) > 1 and term[0] == '@'

    def is_hashtag(self, term):
        return len(term) > 1 and term[0] == '#'

    # text level
    def filter_non_ascii(self, text):
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def filter_twitter_label(self, text):
        if text == '': return text
        out = []
        for term in text.split(' ') :
            if self.is_rt(term) or self.is_url(term) or self.is_at_user(term):
                continue
            if self.is_hashtag(term):
                out.append(term[1:])
            else:
                out.append(term)
        return ' '.join(out)

    def extract_plain_text(self, text):
        text = self.filter_non_ascii(text)
        text = self.filter_twitter_label(text)
        return text
    
    def extract_word_list(self, text):
        text = re.sub(r'[^a-zA-Z]+', ' ', text).strip().lower()
        if text == '': return []
        return text.split(' ')

    # word list level
    def filter_stopword(self, word_list):
        res = []
        for w in word_list:
            if w not in self.stopword_set:
                res.append(w)
        return res
    
    def stem(self, word_list):
        res = []
        porter = nltk.PorterStemmer()
        for w in word_list:
            res.append(porter.stem(w))
        return res

    def extract_distribution(self, word_list):
        res = {}
        for w in word_list:
            if w not in res:
                res[w] = 0 
            res[w] += 1
        length = float(len(word_list))
        for w in res:
            res[w] /= length
        return res

    def extract_tf(self, word_list):
        tf = {}
        for word in word_list:
            if word in tf:
                tf[word] += 1
            else:
                tf[word] = 1
        return tf

    def expand_tf(self, original_tf, additional_tf, idf_dict, K, alpha):
        if len(additional_tf) == 0:
            return original_tf
        # select additional 
        for word in additional_tf:
            if word in idf_dict:
                additional_tf[word] *= idf_dict[word]
            else:
                additional_tf[word] = .0
        additional_lst = sorted(additional_tf.items(), key=lambda item: item[1], reverse=True)
        additional_lst = additional_lst[:K] if len(additional_lst) >= K else additional_lst

        additional_tf = {}
        for item in additional_lst:
            additional_tf[item[0]] = 1

        expanded_tf = {}
        for word in additional_tf:
                expanded_tf[word] = float(additional_tf[word]) * alpha
        for word in original_tf:
                expanded_tf[word] = original_tf[word]

        return expanded_tf


