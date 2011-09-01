class BayesModel:
    def __init__(self):
        self.docs = [0, 0]
        self.word_totals = [0, 0]
        self.word_occs = {}
        self.word_probs = {}

    def add_document(self, document, judgement):
        index = int(judgement)
        self.docs[index] += 1
        words = document.split()
        self.word_totals[index] += len(words)
        for word in words:
            if word not in self.word_occs:
                self.word_occs[word] = [0, 0]
            self.word_occs[word][index] += 1
        self.rebuild_probs()
        print self.word_probs

    def judge(self, document):
        words = document.split()
        # argmax P(v_j)MULT_k(P(word|v_j))
        # P(v_j) = nr docs with judgement v_j / nr_documents
        P_v_j = [self.docs[x] / sum(self.docs) for x in [0,1]]
        test_words = filter(lambda x: x in self.word_probs, words)
        

    def rebuild_probs(self):
        # P(word_k|v_j) = (n_k + 1)/(n + |vocab|)
        # n = nr docs with judgement v_j
        # n_k nr docs word k appears in with judgement v_j
        print self.word_occs
        for word in self.word_occs:
            self.word_probs[word] = [0, 0]
        print self.word_probs
        for t in [0, 1]:
            for word in self.word_occs:
                self.word_probs[word][t] = float(self.word_occs[word][t] + 1) / float(self.word_totals[t] + len(self.word_occs))
        

if __name__ == "__main__":
    model = BayesModel()
    with open('d1.txt', 'r') as doc:
        b = doc.read()
        model.add_document(b, True)
        
