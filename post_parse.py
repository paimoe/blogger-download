import sys, os
from BeautifulSoup import BeautifulSoup as bsoup, Tag
import feedparser

# Regex content fixar
import re
def node(m):
    if m.group(0) == '&lt;':
        return '<'
    else:
        return '>'        
renode = re.compile('&[l|g]t;');

def rd_parse_post(entry):
    blogger_id = entry.id
    created = entry.published.split('.')[:1][0].replace('T', ' ')
    updated = entry.updated.split('.')[:1][0].replace('T', ' ')
    
    link = entry.link#[-1]
    url = link.replace('http://rugbydump.blogspot.com', '')
    title = entry.title.encode('ASCII', 'ignore')
    
    content = entry.summary
    content = renode.sub(node, content).encode('ASCII', 'ignore')

    # Fix up content a bit
    xcontent = bsoup(content)
    img = xcontent.img
    src = img['src'].split('/')[-1]
    img['src'] = '/media/posts/' + src
    img['alt'] = title
    
    
    del(img['border'])
    del(img['style'])
    del(img['id'])        
    
    # Put a centererd paragraph around the image
    np = Tag(xcontent, 'p', [('style', 'text-align: center;')])
    np.insert(0, img)
    
    try:
        xcontent.a.replaceWith(np) # Takes away the link around the first image
    except:
        xcontent.insert(0, np) # Lol that was pretty important (just inserts it and the blank link will remain unfortunately)
    
    # Remove the last div
    xcontent.findAll('div', attrs={'class': 'blogger-post-footer'})[0].extract()
    
    try:
        blurb = xcontent.span.contents[0]
    except:
        blurb = ''
        
    content = xcontent.prettify()
    
    try:
        numcomments = entry.thr_total
    except AttributeError:
        numcomments = 0
        
    try:
        return {
            'src': src,
            'created': created,
            'updated': updated,
            'url': url,
            'numcomments': numcomments,
            'blogger_id': blogger_id,
            'title': title,
            'blurb': blurb,
            'content': content,
        }
    except UnicodeDecodeError:
        print "Skipping post \"%s\".." % title
        return


if 'demo' in sys.argv:
    feed = feedparser.parse('demo.txt')
    
    c = feed.entries[0]
    
    e = rd_parse_post(c)
    
    print e['content']







"""
    
    for i in xml.getElementsByTagName('entry'):
        
        blogger_id = i.getElementsByTagName('id')[0].firstChild.nodeValue
        created = i.getElementsByTagName('published')[0].firstChild.nodeValue.split('.')[:1][0].replace('T', ' ')
        updated = i.getElementsByTagName('updated')[0].firstChild.nodeValue.split('.')[:1][0].replace('T', ' ')
        
        # Use the link thing
        link = i.getElementsByTagName('link')[-1]
        url = link.getAttribute('href').replace('http://rugbydump.blogspot.com', '')
        title = link.getAttribute('title').encode('ASCII', 'ignore')
        
        content = i.getElementsByTagName('content')[0].firstChild.nodeValue
        content = renode.sub(node, content).encode('ASCII', 'ignore')
        
        # Mess with the content a bit yo
        xcontent = bsoup(content)
        img = xcontent.img
        src = img['src'].split('/')[-1]
        img['src'] = '/media/posts/' + src # Should work :(
        img['alt'] = title
        
        del(img['border'])
        del(img['style'])
        del(img['id'])
        
        # Create a new paragraph centered for the image
        np = Tag(xcontent, 'p', [('style', 'text-align: center;')])
        np.insert(0, img)
        #xcontent.insert(0, np)
        
        # Remove last div (footer thing)
        xcontent.findAll('div', attrs={'class': 'blogger-post-footer'})[0].extract()
        
        try:
            blurb = xcontent.span.contents[0]    
        except:
            blurb = ''
        
        content = xcontent.prettify()
        
        try:
            numcomments = i.getElementsByTagName('thr:total')[0].firstChild.nodeValue   
        except IndexError:
            numcomments = 0
        
        try:
            final += post_xml % (
                src,
                created,
                updated,
                url,
                numcomments,
                blogger_id,
                title,
                blurb,
                content,
            )
        except UnicodeDecodeError:
            print "\"%s\", skipping..." % title
            count += 1
            continue
        """
