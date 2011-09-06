import fractions 


class FractionProbs:
    def compute_prob(self, num, denom):
        return fractions.Fraction(num, denom)

class FloatProbs:
    def compute_prob(self, num, denom):
        return float(num)/denom
        
class BayesModel(FractionProbs):
    def __init__(self, classes):
        self.classes = classes
        self.docs = dict([(c, 0) for c in classes])
        self.word_totals = dict([(c, 0) for c in classes])
        self.word_occs = {}
        self.word_probs = {}

    def add_document(self, document, doc_class):
        index = doc_class 
        # Increment # docs with doc_class j
        if not index in self.docs:
            self.docs[index] = 0
        self.docs[index] += 1
        words = document.split()
        # Increment position totals for docs of doc_class j
        if not index in self.word_totals:
            self.word_totals[index] = 0
        self.word_totals[index] += len(words)
        # Update word occurences
        for word in words:
            if word not in self.word_occs:
                self.word_occs[word] = dict([(c, 0) for c in self.classes])
            if not index in self.word_occs[word]:
                self.word_occs[word][index] = 0
            self.word_occs[word][index] += 1
        # Rebuild probabilties from occurances
        #   If a lot of documents are going to be trained at once, this should be delayed
        self.rebuild_probs()

    def rebuild_probs(self):
        # Init probabilities
        for word in self.word_occs:
            self.word_probs[word] = {}
        for j in self.docs:
            # Estimate P(word_k|v_j) = (n_k + 1)/(n + |vocab|)
            # self.compute_prob is provided by a mixin class
            for word in self.word_occs:
                self.word_probs[word][j] = self.compute_prob(self.word_occs[word][j] + 1,   
                                                             self.word_totals[j] + len(self.word_occs))
        
    def classify(self, document):
        # classification = argmax_j P(v_j) * MULT_k(P(word|v_j))
        words = document.split()
        # Only look at words that appear in the vocabulary
        test_words = filter(lambda x: x in self.word_probs, words)
        args = {}
        # Estimate the priors for P(v_j) * MULT_k(P(word|v_j))
        for j in self.docs:
            # estimate P(v_j)
            post = self.compute_prob(self.docs[j], sum(self.docs.values()))
            # estimate MULT_k(P(word|v_j))
            _word_probs = [self.word_probs[word][j] for word in test_words]
            nums = [x.numerator for x in _word_probs] or [1]
            denoms = [x.denominator for x in _word_probs] or [1]
            num = reduce(lambda x, y: x*y, nums)
            denom = reduce(lambda x, y: x*y, denoms)
            post *= self.compute_prob(num, denom)
            args[j] = post
        # Normalize
        s = sum(args.values())
        for k in args:
            args[k] = args[k] / s
            args[k] = args[k].limit_denominator()
        # Argmax
        inv = [(v, k) for k, v in args.items()]
        inv.sort()
        inv.reverse()
        # Return [winning_class, [class probs]]
        return [inv[0][1], args]

if __name__ == "__main__":
    model = BayesModel([True, False])
    with open('yes.txt', 'r') as doc:
        b = doc.read()
        model.add_document(b, True)
    with open('no.txt', 'r') as doc:
        b = doc.read()
        model.add_document(b, False)
    with open('d1.txt', 'r') as doc:
        b = doc.read()
    print model.classify(b)
        
