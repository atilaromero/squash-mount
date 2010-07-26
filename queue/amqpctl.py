#!/bin/env python

import amqplib.client_0_8 as amqpclient

class wchannel:
    def __enter__(self):
        self.conn=amqpclient.Connection(host='localhost:5672')
        self.chan=self.conn.channel()
        return self.chan
    def __exit__(self,type,value,traceback):
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
        
def consume(queue, function, consumer_tag):
    with wchannel() as chan:
        def recv_callback(msg):
            function(msg.body)
            chan.basic_ack(msg.delivery_tag)
        chan.basic_consume(queue=queue,
                           callback=recv_callback,
                           consumer_tag=consumer_tag)
        try:
            while True:
                chan.wait()
        finally:
            chan.basic_cancel(consumer_tag)

def publish(s,queue):
    with wchannel() as chan:
        msg=amqpclient.Message(s)
        chan.basic_publish(msg,exchange=queue,routing_key=queue)

