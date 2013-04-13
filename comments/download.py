import urllib2

import sys
import time
import os

import MySQLdb as sql

# Select post IDs
# Demo: tag:blogger.com,1999:blog-32316390.post-1712101221610946611 from posts.blogger_id
db = sql.connection(host="localhost", user="root", passwd="a", db="rugbydump")
db.query("SELECT blogger_id, post_title FROM posts")
r = db.store_result()

posts = []

for row in r.fetch_row(maxrows=0):
    _Id = row[0]
    
    # [todo] skip if its a normal non-blogger comment (at least for testing) so it doesn't f'up, it won't be able to split
    
    _Id = _Id.split('-')[2:][0]
    posts.append(_Id)

# 
proper_url = 'http://rugbydump.blogspot.com/feeds/%s/comments/default?max-results=600'
whatisthisvar = 1
failed = []

def get_feed(post_id):
    url = proper_url % post_id
    
    print "Opening %s" % url
    
    try:
        o = urllib2.urlopen(url)
    except:
        time.sleep(10)
        failed.append(post_id)
        return
    
    open_file = open('each_post/%s.xml' % post_id, 'w')
    open_file.write( o.read() )
    
    open_file.close()
    o.close()
    
    print "Done %s" % post_id

# Re-Download any specific posts instead of all of them
if 'also' in sys.argv:
    ids = sys.argv[2].split(',')
    for id in ids:
        get_feed(id)
        
    if len(failed) > 0:
        print "Failed on: " + failed.join(',')
        for f in failed:
            print f
        
    sys.exit(0)

# Main loop
for x in posts:    
    
    # I forgot why this is here, but it was apparently an issue
    if os.path.exists('each_post/store/%s.xml' % x) == True:
        print "Skipping %s" % whatisthisvar
        whatisthisvar += 1
        continue
    
    get_feed(x)
    
    print "%d: %s" % (whatisthisvar, x)
    
    whatisthisvar += 1

print "Complete"

if len(failed) > 0:
    print "Failed on: " + failed.join(',')
    for f in failed:
        print f
        
sys.exit(0)
