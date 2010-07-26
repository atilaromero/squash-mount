#!/bin/env python

import amqplib.client_0_8 as amqpclient

def recv_callback(msg):
    print 'Received: ' + msg.body

def consume():
    conn=amqpclient.Connection(host='localhost:5672',
                               userid='guest',
                               password='guest',
                               virtual_host='/',
                               insist=False)
    chan=conn.channel()
    
    chan.queue_declare(queue='po_box',
                       durable=False,
                       exclusive=False, auto_delete=False)
    
    chan.exchange_declare(exchange="sorting_room",
                          type="direct",
                          durable=False,
                          auto_delete=False,)
    
    chan.queue_bind(exchange="sorting_room",
                    routing_key="jason",
                    queue="po_box")
    
    chan.basic_consume(queue='po_box',
                       no_ack=True,
                       callback=recv_callback,
                       consumer_tag="testtag")
    while True:
        chan.wait()
    
#chan.basic_cancel("testtag")
