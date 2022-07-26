import glob
import os

import re
import yake
from pylatexenc.latex2text import LatexNodes2Text

import gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument, Word2Vec
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import ngrams

text = []

#globing our books
folder = 'books/openintro-statistics/'
books = glob.glob(folder + "**/*.tex", recursive=True)

#set stopwords
stop_words = set(stopwords.words('english'))
processed_text = []

#get our training books
for i, b in enumerate(books) :
    f = open(b, "r")
    text.append(LatexNodes2Text().latex_to_text(f.read().lower()))
tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(text)]

for t in text:
    tokens = word_tokenize(t)
    filtered = [w for w in tokens if not w in stop_words and re.search("[^\w\s-]", w) == None]
    processed_text.append(filtered)

print(processed_text)

#training Doc2Vec
model = Doc2Vec()
model.build_vocab(tagged_data)
model.train(tagged_data, total_examples=model.corpus_count, epochs=50)
model.save("doc2vec_openintro-statistics.bin")
print(f"most similar from 0 is {model.docvecs.most_similar([0])}")
#Word2Vec
model2 = Word2Vec()
model2.build_vocab(processed_text)
model2.train(processed_text, total_examples=model.corpus_count, epochs=50)
model2.save("word2vec_openintro-statistics.bin")

#infer vectors on remaining books
for i, b in enumerate(books):
    if i>=5:
        print(b)
        f = open(b, "r")
        tokenized = LatexNodes2Text().latex_to_text(f.read().lower()) 
        text = word_tokenize(tokenized)
        print(model.infer_vector(text))

print("vocab word2vec")
print(len(model2.wv.index_to_key))
print(model2.wv.index_to_key)
