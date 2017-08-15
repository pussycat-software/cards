#!/usr/bin/env python3

import sys
from japronto import Application
import yaml
import json
import random
import time
import hashlib
import redis

from lib.decks import Decks

def config_load(fname='./config.yml'):
    return yaml.load(open(fname).read())

def help_show(request):
    help_text = open('./res/help.txt').read()

    return request.Response(text=help_text)

def game_new(request):
    try:
        deck_type = request.match_dict['deck_type']
    except:
        deck_type = config['game']['default_type']

    if deck_type in ('ru', 'russian'):
        cards = list(decks.russian)
    elif deck_type in ('fr', 'french'):
        cards = list(decks.french)
    else:
        return request.Response(code=400)

    card = random.choice(cards)
    cards.remove(card)

    m = hashlib.md5()
    deck_id = '%s_%f' % (
        request.remote_addr,
        time.time()
    )
    m.update(deck_id.encode())
    deck_id = m.hexdigest()

    response = {
        'id': deck_id,
        'type': deck_type,
        'card': card,
        'left': len(cards)
    }

    redis_handler.set(deck_id, json.dumps(cards))
    redis_handler.expire(deck_id, config['redis']['ttl'])

    return request.Response(text=str(response))

def game_resume(request):
    deck_id = request.match_dict['deck_id']

    try:
        cards = json.loads(redis_handler.get(deck_id).decode())
    except:
        cards = []

    if len(cards) > 0:
        card = random.choice(cards)
        cards.remove(card)

        redis_handler.set(deck_id, json.dumps(cards))
        redis_handler.expire(deck_id, config['redis']['ttl'])
    else:
        card = None

    response = {
        'id': deck_id,
        'card': card,
        'left': len(cards)
    }

    return request.Response(text=str(response))

if __name__ == '__main__':
    config_fname = sys.argv[1] if len(sys.argv) >= 2 else None

    try:
        config = config_load(config_fname)
    except:
        print('Error, could not load config')
        print('Usage:\n\t./%s [./config.yml]' % (sys.argv[0]))
        sys.exit(1)

    decks = Decks()

    redis_handler = redis.Redis(
        host=config['redis']['host'],
        port=config['redis']['port'],
        password=config['redis']['password']
    )

    app = Application()

    app.router.add_route('/', help_show)
    app.router.add_route('/game/new/', game_new)
    app.router.add_route('/game/new/{deck_type}/', game_new)
    app.router.add_route('/game/{deck_id}/', game_resume)

    app.run(
        debug=config['debug'],
        host=config['listen']['host'],
        port=config['listen']['port']
    )
