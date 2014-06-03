imentor
=======

Python wrapper for scraping iMentor data

[https://imentor.imentorinteractive.org](https://imentor.imentorinteractive.org)


## Basic Usage

Creating a client:

    c = Client("email@example.com", "password123")

Using the client to read messages:

    messages = c.get_messages()
    for m in messages:
        print m

Getting specific information about a message:

    m = messages[0]
    print m.subject
    print m.from_
    print m.content
    print m.datetime

## About:

Uses `message/list/` URL endpoint for getting a list of messages.

Uses `message/view/<message_id>/` URL endpoint for getting information specific to a message.
