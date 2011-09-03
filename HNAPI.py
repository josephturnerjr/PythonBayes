import urllib2
import re
import UrlText
import time
import BayesModel
import os
import pickle

# every hour, grab the new feed and update the list
# then grab the front page and promote any items that made it
# after a certain number of steps, retire any old non-frontpage items as won't-make-its

class HNFollower:
    def __init__(self):
        self.url = "http://news.ycombinator.com"
        self.new_url = self.url + "/newest"
        self.undecided = {}
        # Init the model, seed with initial values
        self.model = BayesModel.BayesModel([True, False])
        for seed in [['yes.txt', True], ['no.txt', False]]:
            with open(seed[0], "r") as d:
                doc = d.read()
                self.model.add_document(doc, seed[1])
        self.correct = 0
        self.total_predicted = 0
        self.expire_time = 3600 * 2
        self.seen = {}
        
    def update_new(self):
        print "Retrieving article list"
        articles = self.parse_page(self.new_url)
        for new in articles:
            if new not in self.undecided and new not in self.seen:
                print "Trying to add [%s: %s] to undecided" % (new, articles[new])
                try:
                    article_text = UrlText.get_url_text(articles[new])
                    self.undecided[new] = {'url': articles[new],        
                                           'text': article_text, 
                                           'time': time.time(), 
                                           'class': self.model.classify(article_text)}
                except Exception, e:
                    print "Error adding", e
        
    def update_classifications(self):
        print "Retrieving frontpage"
        front = self.parse_page(self.url)
        now = time.time()
        to_remove = []
        for a in self.undecided:
            doc = self.undecided[a]
            if a in front:
                print "Found on frontpage:", doc['url']
                if doc['class'][0] == True:
                    self.total_predicted += 1
                    self.correct += 1
                self.model.add_document(doc['text'], True)
                to_remove.append(a)
            elif now - doc['time'] > self.expire_time:
                print "Expired:", doc
                if doc['class'][0] == False:
                    self.total_predicted += 1
                    self.correct += 1
                self.model.add_document(doc['text'], False)
                to_remove.append(a)
        print "Removing these:", to_remove
        for a in to_remove:
            self.seen[a] = self.undecided[a]
            del self.undecided[a]
        c = float(self.correct) / (self.total_predicted or 1)
        print "After update, correctness is", c

    def parse_page(self, url):
        print "Getting feed"
        new_feed = urllib2.urlopen(url)
        new = " ".join(new_feed.read().split("\n"))
        print "Scraping for URLs and IDs"
        regex = re.compile("<td class=\"title\">.*?<a href=\"(.*?)\".*?<td class=\"subtext\".*?<a href=\"item\?id=(\d*?)\"")
        return dict([[y,x] for x,y in regex.findall(new)])

    def update(self):
        self.update_new()
        self.update_classifications()
        
    
FOLLOWER_PICKLE = "follower.pickle"
def create_follower():
    if os.path.exists(FOLLOWER_PICKLE):
        with open(FOLLOWER_PICKLE, "rb") as p:
            print "Reading follower from pickle"
            return pickle.load(p)
    print "Creating follower"
    return HNFollower()

def main():
    a = create_follower()    
    a.update()
    with open(FOLLOWER_PICKLE, "wb") as p:
        print "Dumping follower to pickle"
        return pickle.dump(a, p)
    
if __name__ == "__main__":
    main()
