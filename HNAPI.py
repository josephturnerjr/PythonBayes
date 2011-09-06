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
        self.promoted = {}
        self.expired = {}
        self.skipped = {}
        self.scrape_regex = re.compile("<td class=\"title\">.*?<a href=\"(.*?)\".*?<td class=\"subtext\".*?<a href=\"item\?id=(\d*?)\"")
        
    def update_new(self, articles):
        # Update the undecided list based on articles on the new page
        for new in articles:
            if new not in self.undecided and \
               new not in self.promoted and \
               new not in self.expired and \
               new not in self.skipped:
                print "Trying to add [%s: %s] to undecided" % (new, articles[new])
                # Skip internal links 
                if not "://" in articles[new]:
                    self.skipped[new] = articles[new]
                else:
                    try:
                        # Retrieve article text as a word string
                        article_text = UrlText.get_url_text(articles[new])
                        # Add the article, along with the Bayesian prediction
                        self.undecided[new] = {'url': articles[new],        
                                               'text': article_text, 
                                               'time': time.time(), 
                                               'class': self.model.classify(article_text)}
                    except Exception, e:
                        print "Error adding", e
        
    def update(self):
        print "Retrieving new article list"
        page = self.retrieve_page(self.new_url)
        self.update_new(self.parse_page(page))
        
        print "Retrieving frontpage"
        _p= self.retrieve_page(self.url)
        front = self.parse_page(_p)
        # Grab the time for expiration 
        now = time.time()
        promoted = []
        expired = []
        for a in self.undecided:
            doc = self.undecided[a]
            # Promote articles that make it to the frontpage
            if a in front:
                print "Found on frontpage:", doc['url']
                print doc['class'][0]
                self.total_predicted += 1
                # Update the stats
                if doc['class'][0] == True:
                    print "Success!"
                    self.correct += 1
                self.model.add_document(doc['text'], True)
                promoted.append(a)
            # Expire articles that have been sitting around too long
            elif now - doc['time'] > self.expire_time:
                print "Expired:", doc['url']
                print doc['class'][0]
                self.total_predicted += 1
                # Update the stats
                if doc['class'][0] == False:
                    print "Success!"
                    self.correct += 1
                self.model.add_document(doc['text'], False)
                expired.append(a)
        # Remove decided articles from the undecided list
        #   Can't do this in the above loop, would change dict size
        print "Removing these:", promoted + expired
        for a in promoted:
            self.promoted[a] = self.undecided[a]
            del self.undecided[a]
        for a in expired:
            self.expired[a] = self.undecided[a]
            del self.undecided[a]

        self.write_output_page(page)

    def write_output_page(self, page):
        # Calculate internal stats
        if self.total_predicted != 0:
            c = float(self.correct) / (self.total_predicted)
        else: 
            c = 0.0
        stat_str = "<div style='margin-top: 16px; width: 85%;'>"
        stat_str += "<div style='float: left; width: 50%; text-align: left;'>"
        stat_str += "<h1>Bayes News</h1>"
        stat_str += "<p>Uses a dead-simple naive Bayes classifier to predict whether submitted articles will make it to the Hacker News frontpage. The predicted probability of making it to the frontpage is presented just to the left of the point count for the article. Articles that have already made it are marked as 'MADE IT'; articles that have gone too long without making it are marked as 'EXPIRED'. For some reason, HN-internal articles are skipped.</p>"
        stat_str += "<p><i>Predicted %d articles correctly out of %d seen (%0.2f%%)<i></p>" % (self.correct, self.total_predicted, 100.0 * c)
        stat_str += "<p><i>Chance correctness would be %0.2f%%</i></p>" % (100.0 * float(len(self.promoted)) / (len(self.promoted) + len(self.expired)),)
        stat_str += "</div></div>"
        page = re.sub("<body><center>", "<body><center>" + stat_str, page)
        
        for i in self.undecided:
            true_rat = self.undecided[i]["class"][1][True].limit_denominator(10000)
            true_pct = 100.0 * float(true_rat.numerator) / true_rat.denominator
            page = re.sub("<span id=score_" + i + ">", "<b>" + ("%0.2f" % true_pct) + "</b> <span id=score_" + i + ">", page)
        for i in self.promoted:
            page = re.sub("<span id=score_" + i + ">", "<b>MADE IT</b> <span id=score_" + i + ">", page)
        for i in self.expired:
            page = re.sub("<span id=score_" + i + ">", "<b>TOO LATE</b> <span id=score_" + i + ">", page)
        for i in self.skipped:
            page = re.sub("<span id=score_" + i + ">", "<b>SKIPPED</b> <span id=score_" + i + ">", page)

        print "Writing output page"
        with open("out.html", "w") as out:
            out.write(page)

    def retrieve_page(self, url):
        print "Retrieving page", url
        
        new_feed = urllib2.urlopen(url, timeout=25)
        return " ".join(new_feed.read().split("\n"))

    def parse_page(self, page):
        print "Scraping for URLs and IDs"
        return dict([[y,x] for x,y in self.scrape_regex.findall(page)])

    
FOLLOWER_PICKLE = "follower.pickle"
def create_follower():
    if os.path.exists(FOLLOWER_PICKLE):
        with open(FOLLOWER_PICKLE, "rb") as p:
            print "Reading follower from pickle"
            return pickle.load(p)
    print "Creating follower"
    return HNFollower()

def save_follower(follower):
    with open(FOLLOWER_PICKLE, "wb") as p:
        print "Dumping follower to pickle"
        pickle.dump(follower, p)

def main():
    a = create_follower()    
    for i in range(1000):
        try:
            a.update()
            save_follower(a)
        except Exception, e:
            print "Error updating", e
        time.sleep(5 * 60)
    
if __name__ == "__main__":
    main()
