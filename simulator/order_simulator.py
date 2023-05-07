"""Process orders and write to database"""

from datetime import datetime
import json
import logging
import sys

import simpy

from db.connection import (
    css_cursor,
    execute_sql,
)
from db.migrations.create_orders_table import recreate_orders_table
from parameters.simulation_parameters import (
    NUM_COOKS,
    SIMULATION_SPEED,
)

# configure logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(
    logging.StreamHandler(sys.stderr)
)

# loading data
with open('data/orders.json') as f:
    orders = json.load(f)
with open('data/items.json') as f:
    menu = json.load(f)

# transform items into cook time lookup
cook_times = {i['name']:i['cook_time'] for i in menu}


def get_time(ts):
    """Parse timestamps into epochs; ignore fractional seconds"""
    ts_parts = ts.split('.')
    return int(datetime.strptime(ts_parts[0], '%Y-%m-%dT%H:%M:%S').timestamp())

# seconds before first order to start simulation
TIME_BUFFER = 10
tstamps = [get_time(order['ordered_at']) for order in orders]
ENV_START = min(tstamps) - TIME_BUFFER


class Kitchen(object):

    def __init__(self, env, num_cooks):
        self.env = env
        self.resources = simpy.Resource(env, num_cooks)
        self.orders_started = []

    def prepare_food(self, order_id, cook_time):

        if order_id not in self.orders_started:
            self.orders_started.append(order_id)
            update_db_order_started(self.env, order_id)
        yield self.env.timeout(cook_time)


def request_item(env, order, item, kitchen):
    with kitchen.resources.request() as request:
        yield request
        yield env.process(kitchen.prepare_food(order['id'], cook_times[item['name']]))

def process_order(env, order, kitchen):
    yield env.timeout(get_time(order['ordered_at'])-ENV_START)
    if not order['items']:
        log.info(f"Order {order['id']} has no items and will not be processed")
        return
    update_db_order_received(env, order)
    events = []
    for item in order['items']:
        for _ in range(item['quantity']):
            events.append(env.process(request_item(env, order, item, kitchen))) 
    yield env.all_of(events)
    update_db_order_completed(env, order['id'])


def update_db_order_received(env, order):
    SQL = f"""
    INSERT INTO orders (id, status, received_at, customer_name, service, total_price, items)
    VALUES (
        {order['id']}
        , 'Queued'
        , {env.now}
        , '{order['name']}'
        , '{order['service']}'
        , {sum([i['price_per_unit'] * i['quantity'] for i in order['items']])}
        , '{json.dumps({i['name'].replace("'", "''"):i['quantity'] for i in order['items']})}'
    );
    """
    with css_cursor() as cur:
        execute_sql(SQL, cur)


def update_db_order_started(env, order_id):
    SQL = f"""
    UPDATE orders
    SET started_at = {env.now}
    , status = 'In Progress'
    WHERE id = {order_id};
    """
    with css_cursor() as cur:
        execute_sql(SQL, cur)


def update_db_order_completed(env, order_id):
    SQL = f"""
    UPDATE orders
    SET completed_at = {env.now}
    , status = 'Completed'
    WHERE id = {order_id};
    """
    with css_cursor() as cur:
        execute_sql(SQL, cur)

def simulate_orders(orders, speed=SIMULATION_SPEED, num_cooks=NUM_COOKS):
    recreate_orders_table()
    env = simpy.rt.RealtimeEnvironment(
        initial_time=ENV_START,
        factor=1/speed,
        strict=False,
    )
    kitchen = Kitchen(env, num_cooks=num_cooks)
    for idx, order in enumerate(orders):
        order['id'] = idx+1
        env.process(process_order(env, order, kitchen))

    log.info(f"Starting simulation at speed {speed}X with {num_cooks} cooks")
    env.run()


if __name__ == '__main__':
    simulate_orders(orders)
