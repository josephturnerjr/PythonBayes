import urllib2
import re
    
def get_url_text(url):
    req = urllib2.Request(url, headers={'User-agent': "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"})
    page = urllib2.urlopen(req, timeout = 25)
    
    a = " ".join(page.read().split('\n'))
    re.DOTALL=True
    for tag in ["script", "style"]:
        a = re.sub("<"+tag+"[^>]*>(.*?)</"+tag+">", "", a)
    a = re.sub("<[^>]*>", "", a)
    a = re.sub("&.*?;", "", a)
    glob = " ".join(re.findall("\w+[a-zA-Z]+", a))
    return glob.lower()


if __name__ == "__main__":
    with open('yes.txt', 'w') as a:
        a.write(get_url_text("http://www.jwz.org/blog/2011/09/surprise-facebook-doesnt-like-privacy-countermeasures/"))
    with open('no.txt', 'w') as a:
        a.write(get_url_text("http://vishwasbabu.blogspot.com/2011/09/learning-to-let-go-technology-to-rescue.html"))

