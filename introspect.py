import HNAPI
from HNAPI import HNFollower
import BayesModel

def print_probs(model):
    a = [(prob[True], word) for word, prob in model.word_probs.items()]
    a.sort()
    a.reverse()
    b = [(prob[False], word) for word, prob in model.word_probs.items()]
    b.sort()
    b.reverse()
    for i in range(200):
        print i, ")", a[i], "\t", b[i]
    
def main():
    f = HNAPI.create_follower()
    print_probs(f.model)

    '''
    model = BayesModel.BayesModel([True, False])
    print " ***** BEFORE ***** "
    print_probs(model)
    for seed in [['yes.txt', True], ['no.txt', False]]:
        with open(seed[0], "r") as d:
            doc = d.read()
            print doc
            model.add_document(doc, seed[1])
            print " ***** DURING ***** "
            print_probs(model)
    '''

    

if __name__ == "__main__":
    main()
