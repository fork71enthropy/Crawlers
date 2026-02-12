from urllib.request import urlopen
from bs4 import BeautifulSoup #pourquoi il refuse ? Il joue à quoi mon editeur vscode ? 

html = urlopen("https://www.univ-lyon1.fr/")
lien_ecole = urlopen("https://www.univ-lyon1.fr/recherche/organisation-et-politique") #lien_ecole est un text_object
bs = BeautifulSoup(lien_ecole.read())
print(bs)