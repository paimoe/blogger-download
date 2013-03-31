blogger-download
================

Couple of scripts to download Blogger posts and add to the database, as well as comments

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

What it did
--------
Looped through all months between 2006 and Sept-ish 2011. Downloaded all posts, extracted the first image, and inserted the image into posts\_media table and the post content into the posts table.
