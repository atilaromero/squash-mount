#!/bin/env python

import amqplib.client_0_8 as amqpclient

class Consumer:
    def __init__(self):
        self.conn=amqpclient.Connection(host='localhost:5672',
#                                   userid='guest',
#                                   password='guest',
#                                   virtual_host='/',
                                   insist=False)
        self.chan=self.conn.channel()
    
    def create_queue(self):
        self.chan.queue_declare(queue='po_box',
                           durable=False,
                           exclusive=False,
                           auto_delete=False)
        
        self.chan.exchange_declare(exchange="sorting_room",
                              type="direct",
                              durable=False,
                              auto_delete=False,)
        
        self.chan.queue_bind(exchange="sorting_room",
                             routing_key="jason",
                             queue="po_box")
        

    def recv_callback(self,msg):
        print 'Received: ' + msg.body
        self.chan.basic_ack(msg.delivery_tag)

    def consume(self):
        self.chan.basic_consume(queue='po_box',
                                callback=self.recv_callback,
                                consumer_tag="testtag")
        try:
            while True:
                self.chan.wait()
        finally:
            self.chan.basic_cancel("testtag")

    def __del__(self):
        self.chan.close()
        self.conn.close()

