import HNAPI
from HNAPI import HNFollower
import BayesModel

def print_probs(model):
    a = [(prob[True], word,(max(prob.values())/min(prob.values())).limit_denominator(100)) for word, prob in model.word_probs.items() if max(prob.values())/min(prob.values()) > 2.0]
    a.sort()
    a.reverse()
    b = [(prob[False], word,(max(prob.values())/min(prob.values())).limit_denominator(100)) for word, prob in model.word_probs.items() if max(prob.values())/min(prob.values()) > 2.0]
    b.sort()
    b.reverse()
    for i in range(200):
        print i, ")", a[i], "\t", b[i]

    
def main():
    f = HNAPI.create_follower()
    print_probs(f.model)
    if f.total_predicted != 0:
        c = 100.0 * float(f.correct) / (f.total_predicted) 
    else: 
        c = 0.0
    print "Correctness is", c, f.correct, f.total_predicted
    print "Chance correctness is", 100.0 * float(len(f.promoted)) / (len(f.promoted) + len(f.expired))

if __name__ == "__main__":
    main()
