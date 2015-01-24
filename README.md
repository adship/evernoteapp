Mininote
========

Mininote is a lightweight note taking app for [Evernote](http://evernote.com) that makes capturing thoughts and other arbitrary information easy and minimally distracting.

In Mininote, notes are single lines of text with inline hashtags; much like Tweets on Twitter.

Notes live in a *mininote* notebook in your Evernote account.

![mininote](/screencast.gif)

Commands
========

Login to your Evernote account:

    mn login

Interact with notes:

    # Add a new note
    mn add "new note #tag"
    
    # Search for notes
    mn search "coffee"

    # Edit notes in a text editor
    # Save and exit the editor to sync your changes
    mn edit "#tag" 

Configure Mininote:

    # Set the text editor for note editing
    mn set-editor "fullpath\wordpad.exe"

Read more about the search syntax [here](https://dev.evernote.com/doc/articles/search_grammar.php#Examples).

Installation
============

Download the source from Github, install Python [2.7.x](https://www.python.org/downloads/) and run:

    python setup.py install

On Windows, you may need to add the *C:\Python27\Scripts* directory to your system path.

Contact
=======

mininoteapp@gmail.com
