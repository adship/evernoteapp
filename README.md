![mininote](/logo.png)

Forget everything you know about note taking apps. Take Twitter style notes with Mininote.

In Mininote, a note is a single line of text with inline hash tags. Think of your notes as a cloud of tagged thoughts.

Notes are stored in a "mininote" notebook in your Evernote account.

Use it
======

Login to your Evernote account:

    mn --login

Interact with notes:

    # Add a new note
    mn
    
    # Search for notes
    mn -q "coffee

    # Edit notes in a text editor
    # Save and exit the editor to sync your changes
    mn -q "coffee" -i

Configure Mininote:

    # Set the text editor for note editing
    mn --set-editor "vim"

Read more about the search syntax [here](https://dev.evernote.com/doc/articles/search_grammar.php#Examples).

Installation
============

Download the source, install Python 2.7 and run:

    python setup.py install

Contact
=======

mininoteapp@gmail.com
