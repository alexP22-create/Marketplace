"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        Thread.__init__(self, **kwargs)

    def run(self):
        for cart in self.carts:
            """ create a cart """
            id_cart = self.marketplace.new_cart()

            for command in cart:
                com_type = command['type']
                product = command['product']
                quantity = command['quantity']

                for _ in range(0, quantity):
                    okk = False

                    if com_type == "add":
                        okk = self.marketplace.add_to_cart(id_cart, product)

                        """ try to add the prod in the cart untill it's possible """
                        while not okk:
                            time.sleep(self.retry_wait_time)
                            okk = self.marketplace.add_to_cart(id_cart, product)

                    if com_type == "remove":
                        self.marketplace.remove_from_cart(id_cart, product)

            """ Get the list of bought products """
            checkout = self.marketplace.place_order(id_cart)

            """ Print the received items: """
            for item in checkout:
                print("{0} bought {1}".format(self.name, item))
