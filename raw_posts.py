from xml.dom import minidom
import sys

import os
import urllib2

import MySQLdb as sql

from datetime import datetime

import feedparser
from post_parse import rd_parse_post

# Download based on dates, because blogger seems to truncate randomly asfnalsfkjnsdlfkjn
dl_url = 'http://www.blogger.com/feeds/32316390/posts/default?published-min=%s&published-max=%s&max-results=500'
dates = [
    ('2006-01-01', '2007-01-01'),
    ('2007-01-01', '2008-01-01'),
    ('2008-01-01', '2009-01-01'),
    ('2009-01-01', '2010-01-01'),
    ('2010-01-01', '2010-02-01'), # Every month now cause theres a limit on the amount blogger shows 
    ('2010-02-01', '2010-03-01'), # January to May 1st
    ('2010-03-01', '2010-04-01'), # January to May 1st
    ('2010-04-01', '2010-05-01'), # January to May 1st
    ('2010-05-01', '2010-06-01'), # June 1st
    ('2010-06-01', '2010-07-01'), # June 1st
    ('2010-07-01', '2010-08-01'), # June 1st
    ('2010-08-01', '2010-09-01'), # September 1st
    ('2010-09-01', '2010-10-01'), # Jan 1st 2011
    ('2010-10-01', '2010-11-01'), # Jan 1st 2011
    ('2010-11-01', '2010-12-01'), # Jan 1st 2011
    ('2010-12-01', '2011-01-01'), # Jan 1st 2011
    ('2011-01-01', '2011-02-01'), # Jan 2011
    ('2011-02-01', '2011-03-01'),
    ('2011-03-01', '2011-04-01'),
    ('2011-04-01', '2011-05-01'),
    ('2011-05-01', '2011-06-01'),
    ('2011-06-01', '2011-07-01'),
    ('2011-07-01', '2011-08-01'),
    
    ('2011-08-01', '2011-09-01'),
    ('2011-09-01', '2011-10-01'), # Final
]

# Loop dates, and download yo
files = []
for d in dates:
    p = 'actual/%s.xml' % d[1]
    files.append(p)
    if 'skipdl' in sys.argv:
        # Continue instead of break so we can still fill the files list, that we loop through later
        continue
    if os.path.exists(p) == False: # i.e. if we already dl'd, skip it
    
        print "Downloading between %s and %s" % (d[0], d[1])
        url = dl_url % (d)
        
        o = urllib2.urlopen(url)
        r = o.read()
        o.close()
        
        f = open(p, 'w')
        f.write( r )
        f.close()
        
        print "Saved %s" % p
    else:
        print "For some reason, isfile(%s) returned True" % p

# Open file and read
fcount = 1

post_xml = "<post image=\"%s\" post_date=\"%s\" last_updated=\"%s\" url=\"%s\" num-comments=\"%s\" blogger=\"%s\"><post_title><![CDATA[%s]]></post_title><post_blurb><![CDATA[%s]]></post_blurb><post_content><![CDATA[%s]]></post_content></post>"

# Select post IDs
# Demo: tag:blogger.com,1999:blog-32316390.post-1712101221610946611 from posts.blogger_id
dbuser = ''
dbpass = ''
dbbase = ''

db = sql.connection(host="localhost", user=dbuser, passwd=dbpass, db=dbbase)
db.query("SELECT last_updated, `blogger_id` FROM posts")
r = db.store_result()
current_posts = {}
    
if 'test' in sys.argv:
    sql_table = 'posts_test'
    do_media = False
    save_file = 'actual/probably_total_test.sql'
else:
    for s in r.fetch_row(maxrows=0):
        current_posts[ s[1] ] = datetime.strptime(s[0], '%Y-%m-%d %H:%M:%S') # 0 = updated, 1 = blogger_id
    sql_table = 'posts'    
    do_media = True
    save_file = 'actual/probably_total.sql'


print "NUM ROWS: %d" % r.num_rows()

queries = []
for fi in files:
    
    feed = feedparser.parse(fi)
    
    print "Opened and read %s, " % fi

    final = ''
    sqldata = []
    count = 1
    
    for entry in feed.entries:
        new_entry = rd_parse_post(entry)
        count += 1
        final += post_xml % (            
            new_entry['src'],
            new_entry['created'],
            new_entry['updated'],
            new_entry['url'],
            new_entry['numcomments'],
            new_entry['blogger_id'],
            new_entry['title'],
            new_entry['blurb'],
            new_entry['content'],
        )
        
        sqldata.append({
            'post_title': new_entry['title'],
            'post_blurb': new_entry['blurb'],
            'post_content': new_entry['content'],
            'post_date': new_entry['created'],
            'last_updated': new_entry['updated'],
            'blogger_url': new_entry['url'],
            'blogger_id': new_entry['blogger_id'],
            'image_uri': new_entry['src'],
        })
        
        if count % 50 == 0:
            print "Done %d" % count
        count += 1

    print "went through %s entries" % count
    print "sqldata: %s" % len(sqldata)

    o = open('actual/raw_posts.parsed.%s.xml' % fcount, 'w')
    try:
        o.write('<?xml version="1.0"?><e>%s</e>' % final)
    except UnicodeEncodeError:
        print "FFFFFFFUUUUUUUUUUUUUUUUUU" + str(len(final))
        sys.exit()   
    o.close()
    
    full = len(sqldata)
    half = full / 2
    sqlcount = 1
    fnum = fcount

    # Now generate SQL file?
    # No wait, first check SQL so we don't duplicate, compare against blogger_id, then idk... check last_updated... yeah that should be good
    # So if it doesn't exist, insert... if it does exist, check if it's been updated, in which case insert
    
    sql = 'INSERT INTO `{0}` (`post_title`, `post_content`, `post_blurb`, `post_date`, `last_updated`, `blogger_url`, `blogger_id`) VALUES '.format(sql_table)
    update_sql = 'UPDATE `{0}` SET `post_title` = "%s", `post_content` = "%s", `post_blurb` = "%s", `last_updated` = "%s", `blogger_url` = "%s" WHERE `blogger_id` = "%s" LIMIT 1;'.format(sql_table)
    fsql = ''
    new_queries = []
    for row in sqldata:
        c = row['post_content'].replace('"', '\\"').replace("rugbydump.blogspot.com", "www.rugbydump.com/index/reverse")
        
        try:
            b = row['post_blurb'].replace('"', '\\"').replace("rugbydump.blogspot.com", "www.rugbydump.com/index/reverse")
        except TypeError:
            b = ''
            
        try:
            t = row['post_title'].replace('"', '\\"')
        except TypeError:
            t = row['post_title']
            
            
        # CHECK IF UPDATED 
        
        action_to_take = 'insert'
        try:
            entered = current_posts[row['blogger_id']]
            #print entered
            if str(entered) != row['last_updated']:
                action_to_take = 'update'
                print "Updating %s because it has been updated since last time" % t
            else:
                # If it is the same, then skip..
                if 'forceupdate' not in sys.argv:
                    print "Skipping %s, already in the database with same last updated time" % t
                    continue
                else:
                    action_to_take = 'update' # Force updating
        except KeyError:
            # If the post doesnt exist, obviously insert
            pass
        
        if action_to_take == 'insert':
            # Insert post_media (do first since it'll be reversed)
            if do_media:
                new_queries.append('INSERT INTO `posts_media` (`post_id`, `image_uri`, `date_added`, `file_name`, `selected`) VALUES ( LAST_INSERT_ID(), "%s", "%s", "%s", "1" ); ' % (row['image_uri'], row['post_date'], row['image_uri']))
            new_queries.append(sql + '("%s", "%s", "%s", "%s", "%s", "%s", "%s"); ' % (t, c, b, row['post_date'], row['last_updated'], row['blogger_url'], row['blogger_id']))
            
        
        else: # If we're updating instead        
            new_queries.append(update_sql % (t, c, b, row['last_updated'], row['blogger_url'], row['blogger_id']))
            
        # It should skip any that are entered, and the same update date
        # It should insert any new ones it has found
        # It should overwrite any old ones, with newer last_updated times
        # Probably skip a huge chunk of them too since yeah probably haven't updated many of the old ones    
            
        # Check and stuff
        #print sqlcount
        sqlcount += 1 # Go through next item in a file
    
    new_queries = new_queries[::-1]
    queries = queries + new_queries
    
    fcount += 1 # Go through next file
    print "finished file"

print "Number of Queries: %d" % len(queries)
    

# Update sql here
if 'nosql' not in sys.argv:

    # All queries stored in $queries
    nsql = open(save_file, 'w')
    nsql.write( "\n".join(queries) )
    nsql.close()  
    print "SQL Written, %d queries saved" % len(queries)
    print "File saved as %s" % save_file
