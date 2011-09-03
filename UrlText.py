import urllib2
import re
    
def get_url_text(url):
    req = urllib2.Request(url, headers={'User-agent': "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"})
    page = urllib2.urlopen(req)
    
    a = " ".join(page.read().split('\n'))
    re.DOTALL=True
    #headers = [x.strip() for x in re.findall("<h\d>(.*?)</h\d>", a)]
    #ps = [x.strip() for x in re.findall("<p[^>]*>(.*?)</p>", a)]
    for tag in ["script", "style"]:
        a = re.sub("<"+tag+"[^>]*>(.*?)</"+tag+">", "", a)
    a = re.sub("<[^>]*>", "", a)
    #glob = " ".join(headers + ps)
    glob = a
    glob = re.sub("\s+", " ", glob)
    return re.sub("<[^>]*>","", glob)


if __name__ == "__main__":
    with open('yes.txt', 'w') as a:
        print get_url_text("http://www.jwz.org/blog/2011/09/surprise-facebook-doesnt-like-privacy-countermeasures/")
    with open('no.txt', 'w') as a:
        print get_url_text("http://vishwasbabu.blogspot.com/2011/09/learning-to-let-go-technology-to-rescue.html")

