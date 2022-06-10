from pylatexenc.latex2text import LatexNodes2Text
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re

nameFile = "book.tex"

f = open(nameFile,"r")

latexParsed = LatexNodes2Text().latex_to_text(f.read().lower())
latexParsed = re.sub(r'http\S+',"",latexParsed)
latexParsed = re.sub("<ref>","",latexParsed).split("\n")

toRemove = ['    < g r a p h i c s >']

cleanList = list(filter(lambda x: x not in toRemove,latexParsed))

idSplit = [0]
for number,line in enumerate(cleanList):
	#This is necessary to cover the case when the line is blank
	try:
		if line[0] == "§":
			idSplit.append(number)		
	except IndexError:
		pass

cleanText = "\n".join(cleanList)
f = open(nameFile+"processed.txt","w")
f.write(cleanText)
f.close()

f = open("kw.txt","w")

vectorizer = CountVectorizer(max_df = 0.90, min_df = 1,stop_words="english",ngram_range=(1, 4))
allkw = []
for i in range(len(idSplit[0:-1])):
	f.write(f"{idSplit[i]},{idSplit[i+1]}\n")
	vector = vectorizer.fit_transform(cleanList[idSplit[i]:idSplit[i+1]])
	print(idSplit[i],"\t",cleanList[idSplit[i]],"\t",idSplit[i+1],"\t",cleanList[idSplit[i+1]])
	lda = LatentDirichletAllocation(n_components=2,random_state=101,max_iter=5)

	lda_fit  = lda.fit(vector)

	for id_value, value in enumerate(lda_fit.components_):
	    f.write(f"The topic would be {id_value}")
	    f.write("\n")
	    lkw = [vectorizer.get_feature_names_out()[index] for index in value.argsort()[-10:]]
	    allkw = allkw + lkw
	    f.write(str(lkw)[1:-2])
	    f.write("\n")
	f.write("-----------------------------------\n")
f.close()
unique_kw = set(allkw)
print(f"Number of kw detected: {len(allkw)}, number of unique kw detected: {len(unique_kw)}")

import gensim.downloader
glove_vectors = gensim.downloader.load('glove-wiki-gigaword-300')

from sklearn.decomposition import PCA
pca = PCA(n_components=2)

one_gram = [kw for kw in unique_kw if len(kw.split(" ")) == 1]
vectors = []
token_not_embedded = []

for kw in one_gram:
	try:
		vectors.append(glove_vectors[kw])
	except KeyError:
		token_not_embedded.append(kw)
print(f"Nombre de token non présents dans le vocabulaire: {len(token_not_embedded)}")

vectors = pca.fit_transform(vectors,None)

import matplotlib.pyplot as plt

fig,ax = plt.subplots()

ax.scatter(vectors[0],vectors[1])

fig.show()


