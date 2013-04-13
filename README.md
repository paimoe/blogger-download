Blogger Post and Comments download
================

Couple of scripts to download Blogger posts and add to the database, as well as comments. It was made because the Blogger XML dump was pretty unusable, and the RSS/atom feeds had a limit to the results.

REALLY hacked together:

- Only works in pretty specific database format
- Completely hand-waves over encoding issues
- No real way to do partial, or steps, mainly in one big go
- commandline spam, with no real options
- Downloads -> stores in XML -> parses XML -> creates SQL files -> manually load using MySQL console

Bottom line, try to avoid using Blogger in the first place if you ever plan to move away from it

Comments
--------
Downloads comments, tries to fix up the times to UTC

Running
--------
    $ python download.py
    $ python raw_posts.py
    
    $ cd comments
    $ python download.py
    $ python parse.py
    
Should fill up a bunch of .sql files to import to MySQL.

AKA not very useful in its current state.

What it did
--------
Looped through all months between 2006 and Sept-ish 2011. Downloaded all posts, extracted the first image, and compiled an sql insert statement: the image went to `posts_media` and post content into `posts`

TODOish
--------
* Cleanup
* Command line options (`$ python run.py --url=example --posts --comments`)
* Cleaner transition from download > sql. Right now it stores it in XML, then re-fetches the XML and parses to form sql inserts, then manually insert. Maybe an option to auto-add to DB.
* Global-er config (db user/pass, url etc)
