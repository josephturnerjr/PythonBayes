import fractions 


class FractionProbs:
    def compute_prob(self, j, word):
        return fractions.Fraction(
                self.word_occs[word][j] + 1, 
                self.word_totals[j] + len(self.word_occs)
            )

class FloatProbs:
    def compute_prob(self, j, word):
        return float(self.word_occs[word][j] + 1) \
                  / float(self.word_totals[j] + len(self.word_occs))
        
class BayesModel(FractionProbs):
    def __init__(self):
        self.docs = [0, 0]
        self.word_totals = [0, 0]
        self.word_occs = {}
        self.word_probs = {}

    def add_document(self, document, judgement):
        # Coerce judgement (currently only booleans) to int for indexing
        #   TODO add capability for multi-judgement
        index = int(judgement)
        # Increment # docs with judgement j
        self.docs[index] += 1
        words = document.split()
        # Increment position totals for docs of judgement j
        self.word_totals[index] += len(words)
        # Update word occurences
        for word in words:
            if word not in self.word_occs:
                self.word_occs[word] = [0, 0]
            self.word_occs[word][index] += 1
        # Rebuild probabilties from occurances
        #   If a lot of documents are going to be trained at once, this should be delayed
        self.rebuild_probs()

    def rebuild_probs(self):
        # Init probabilities
        for word in self.word_occs:
            self.word_probs[word] = [0, 0]
        for j in [0, 1]:
            # Estimate P(word_k|v_j) = (n_k + 1)/(n + |vocab|)
            # self.compute_prob is provided by a mixin class
            for word in self.word_occs:
                self.word_probs[word][j] = self.compute_prob(j, word)
        
    def judge(self, document):
        # classification = argmax_j P(v_j) * MULT_k(P(word|v_j))
        words = document.split()
        # Only look at words that appear in the vocabulary
        test_words = filter(lambda x: x in self.word_probs, words)
        args = []
        # Estimate the priors for P(v_j) * MULT_k(P(word|v_j))
        for j in [0, 1]:
            # estimate P(v_j)
            post = self.docs[j] / sum(self.docs)
            # estimate MULT_k(P(word|v_j))
            word_probs = [self.word_probs[word][j] for word in test_words]
            post *= reduce(lambda x, y: x*y, word_probs)
            args.append(post)
        # Argmax
        return args.index(max(args))

if __name__ == "__main__":
    model = BayesModel()
    with open('d1.txt', 'r') as doc:
        b = doc.read()
    for i in range(1, 100):
        model.add_document(b, True)
    for i in range(1, 100):
        print model.judge(b)
        
