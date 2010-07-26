#!/bin/env python

import amqplib.client_0_8 as amqpclient

class wchannel:
    def __enter__(self):
        self.conn=amqpclient.Connection(host='localhost:5672')
        self.chan=self.conn.channel()
        return chan
    def __exit__(self):
        self.chan.close()
        self.conn.close()
        
  
def create_queue(name):
    with wchannel() as chan:
        chan.queue_declare(queue=name,
                           durable=False,
                           exclusive=False,
                           auto_delete=False)
        
        chan.exchange_declare(exchange=name,
                              type="direct",
                              durable=False,
                              auto_delete=False,)
        
        chan.queue_bind(exchange=name,
                        routing_key=name,
                        queue=name)
        
