import fractions 


class FractionProbs:
    def compute_prob(self, num, denom):
        return fractions.Fraction(num, denom)
        return fractions.Fraction(
            )

class FloatProbs:
    def compute_prob(self, num, denom):
        return float(num)/denom
        return float(self.word_occs[word][j] + 1) \
                  / float(self.word_totals[j] + len(self.word_occs))
        
class BayesModel(FractionProbs):
    def __init__(self, classes):
        self.classes = classes
        self.docs = dict([(c, 0) for c in classes])
        self.word_totals = dict([(c, 0) for c in classes])
        self.word_occs = {}
        self.word_probs = {}

    def add_document(self, document, judgement):
        # Coerce judgement (currently only booleans) to int for indexing
        index = judgement
        # Increment # docs with judgement j
        if not index in self.docs:
            self.docs[index] = 0
        self.docs[index] += 1
        words = document.split()
        # Increment position totals for docs of judgement j
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
        
    def judge(self, document):
        # classification = argmax_j P(v_j) * MULT_k(P(word|v_j))
        words = document.split()
        # Only look at words that appear in the vocabulary
        test_words = filter(lambda x: x in self.word_probs, words)
        args = []
        # Estimate the priors for P(v_j) * MULT_k(P(word|v_j))
        for j in self.docs:
            # estimate P(v_j)
            post = self.compute_prob(self.docs[j], sum(self.docs.values()))
            # estimate MULT_k(P(word|v_j))
            word_probs = [self.word_probs[word][j] for word in test_words]
            post *= reduce(lambda x, y: x*y, word_probs)
            args.append(post)
        # Argmax
        print args
        return args.index(max(args))

if __name__ == "__main__":
    model = BayesModel([0, 1, 2])
    with open('d1.txt', 'r') as doc:
        b = doc.read()
    model.add_document(b, 1)
    print model.judge(b)
        
