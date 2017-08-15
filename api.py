#!/usr/bin/env python3

import sys
from japronto import Application
import yaml
import json
import random
import time
import hashlib
import redis

from lib.cards import Cards

def config_load(fname='./config.yml'):
    return yaml.load(open(fname).read())

def help_show(request):
    help_text = open('./res/help.txt').read()

    return request.Response(text=help_text)

def game_new(request):
    game_type = request.match_dict['type']
    if game_type in ('ru', 'russian'):
        cards = list(Cards.russian)
    elif game_type in ('fr', 'french'):
        cards = list(Cards.french)
    else:
        return request.Response(code=400)

    card = random.choice(cards)
    cards.remove(first_card)

    m = hashlib.md5()
    game_id = '%s_%f' % (
        request.remote_addr,
        time.time()
    )
    m.update(game_id.encode())
    game_id = m.hexdigest()

    response = {
        'type': game_type,
        'card': card,
        'id': game_id,
        'cards_left': len(cards)
    }

    redis_handler.set(game_id, json.dumps(cards))
    redis_handler.expire(game_id, config['redis']['ttl'])

    return request.Response(text=str(response))

def game_resume(request):
    game_id = request.match_dict['game_id']

    try:
        cards = json.loads(redis_handler.get(game_id).decode())
    except:
        cards = []

    if len(cards) > 0:
        card = random.choice(cards)
        cards.remove(new_card)

        redis_handler.set(game_id, json.dumps(cards))
        redis_handler.expire(game_id, config['redis']['ttl'])
    else:
        card = None

    response = {
        'card': card,
        'id': game_id,
        'cards_left': len(cards)
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

    redis_handler = redis.Redis(
        host=config['redis']['host'],
        port=config['redis']['port'],
        password=config['redis']['password']
    )

    app = Application()

    app.router.add_route('/', help_show)
    app.router.add_route('/new/{type}/', game_new)
    app.router.add_route('/game/{game_id}/', game_resume)

    app.run(
        debug=config['debug'],
        host=config['listen']['host'],
        port=config['listen']['port']
    )
