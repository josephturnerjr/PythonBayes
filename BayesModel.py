import fractions 

class BayesModel:
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
        for t in [0, 1]:
            # Estimate P(word_k|v_j) = (n_k + 1)/(n + |vocab|)
            # TODO add mixins to determine whether to use fractions or floats for this 
            #   (floats don't work on low numbers of training docs)
            for word in self.word_occs:
                self.word_probs[word][t] = fractions.Fraction(
                                                    self.word_occs[word][t] + 1, 
                                                    self.word_totals[t] + len(self.word_occs)
                                                )
        
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
    model.add_document(b, True)
    print model.judge(b)
        
