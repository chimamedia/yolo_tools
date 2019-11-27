import os

l = ["bottle","can","potato","red","yellow"]

for word in l:
    os.system("convert -fill black -background white -bordercolor white -border 4 -font futura-normal -pointsize 18 label:\"%s\" \"%s.png\""%(word, word))
