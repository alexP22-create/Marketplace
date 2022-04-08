"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from pickle import TRUE
from threading import Thread
import time

class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.id_prod = -1
        Thread.__init__(self, **kwargs)

    def run(self):
        self.id_prod = self.marketplace.register_producer()

        while TRUE:
            okk = False

            for (product, quantity, prod_time) in self.products:
                for _ in range(0, quantity):
                    """ create and publish the product """
                    time.sleep(prod_time)
                    okk = self.marketplace.publish(self.id_prod, product)

                    """ while publishing fails try untill it will stop failing """
                    while not okk:
                        time.sleep(self.republish_wait_time)
                        okk = self.marketplace.publish(self.id_prod, product)
