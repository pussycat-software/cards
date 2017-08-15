# What is it

This is an API to provide card dealing routines for couple of my JavaScript-based gaming projects.

It just gives out cards.

# Usage

```
GET     /deal/new/

    start new game of default type
    set such in config file

GET     /deal/new/fr/

    start new french deck game
    52 cards
    from 2 to Aces, no Jokers

GET     /deal/new/ru/

    start new russian deck game
    36 cards
    from 6 to Aces, no Jokers

GET     /deal/{deck_id}/

    resume an old game
```

Each card given is encoded with 2-symbols:

```
2h - 2 of Hearts
6d - 6 of Diamonds
jc - Jack of Clubs
as - Ace of Spades
```

You also would get number of cards remaining in the deck.

Notice, that there is no deck type information stored in deck data. You should save this information at the moment of preforming your first request.

Watch out, old games data is erased after default TTL of 1 hour expired.

## Examples

Following example is using [httpie](https://httpie.org/):

```
$ http http://cards/deal/new/
HTTP/1.1 200 OK
{'type': 'fr', 'card': '4h', 'id': 'c727058430d21b07f9e90795e64ef401', 'left': 51}

$ http http://cards/deal/c727058430d21b07f9e90795e64ef401/
HTTP/1.1 200 OK
{'card': 'ks', 'id': 'c727058430d21b07f9e90795e64ef401', 'left': 50}

# Requesting more cards ...

$ http http://cards/deal/c727058430d21b07f9e90795e64ef401/
HTTP/1.1 200 OK
{'card': '4h', 'id': 'c727058430d21b07f9e90795e64ef401', 'left': 0}

$ http http://cards/deal/c727058430d21b07f9e90795e64ef401/
HTTP/1.1 200 OK
{'card': None, 'id': 'c727058430d21b07f9e90795e64ef401', 'left': 0}
```

# Installation

## Docker-based

It's possible to run all the instances inside the containers, to do so one would need:

- Docker
  - docker-compose

The algorithm is as simple as:

```
git clone ... ./cards
cd ./cards
docker-compose up
```

## Local instance

This is more complicated installation method, one would need some packages and database instance:

- Python 3
  - japronto
  - json, yaml
  - redis
- Redis

Running an API instance would then look like so (Redis instance considered to be up and ready):

```
git clone ... ./cards
cd ./cards
pip3 install -r requirements.txt
cp config.yml.example config.yml
./api.py
```
