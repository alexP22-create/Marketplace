"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
import unittest
import logging
from logging.handlers import RotatingFileHandler
import time

class TestMarketplace(unittest.TestCase):
    def setUp(self):
        """ marketplace declaration along with a list of 2 products """
        self.marketplace = Marketplace(1)
        self.products = []

        pr1 = product.Product
        pr1.name = "Lipton"
        pr1.price = 5
        pr2 = product.Product
        pr2.name = "Jacobs"

        pr2.price = 12
        self.products.append(pr1)
        self.products.append(pr2)

    def test_register_producer(self):
        pr1 = self.marketplace.register_producer()
        pr2 = self.marketplace.register_producer()
        """ check the id of the publishers """
        self.assertEqual(pr1, 0)
        self.assertEqual(pr2, 1)

    def test_publish(self):
        pr1 = self.marketplace.register_producer()
        pr2 = self.marketplace.register_producer()

        okk = self.marketplace.publish(pr1, self.products[0])
        self.assertEqual(okk, True)
        okk = self.marketplace.publish(pr2, self.products[1])
        self.assertEqual(okk, True)
        """ when there is no more room for profucts to be published """
        okk = self.marketplace.publish(pr1, self.products[0])
        self.assertEqual(okk, False)

        """ check the published products """
        self.assertEqual(self.marketplace.products[pr1][0], self.products[0])
        self.assertEqual(self.marketplace.products[pr2][0], self.products[1])

    def test_new_cart(self):
        cr1 = self.marketplace.new_cart()
        cr2 = self.marketplace.new_cart()
        """ check the card id of every consumer """
        self.assertEqual(cr1, 0)
        self.assertEqual(cr2, 1)

    def test_add_to_cart(self):
        self.marketplace.publish(0, self.products[0])
        self.marketplace.publish(1, self.products[1])
        cr1 = self.marketplace.new_cart()
        cr2 = self.marketplace.new_cart()

        okk = self.marketplace.add_to_cart(cr1, self.products[0])
        self.assertEqual(okk, True)
        """ when the consumer is not registered to the market """
        okk = self.marketplace.add_to_cart(3, self.products[0])
        self.assertEqual(okk, False)
        okk = self.marketplace.add_to_cart(cr2, self.products[1])
        self.assertEqual(okk, True)

        """ check the products in the cart """
        prod = self.marketplace.carts[cr1][0][1]
        self.assertEqual(self.products[0], prod)
        prod = self.marketplace.carts[cr2][0][1]
        self.assertEqual(self.products[1], prod)

    def test_remove_from_cart(self):
        cr1 = self.marketplace.new_cart()
        self.marketplace.publish(0, self.products[0])
        self.marketplace.publish(1, self.products[1])

        self.marketplace.add_to_cart(cr1, self.products[0])
        okk = self.marketplace.remove_from_cart(cr1, self.products[0])
        self.assertEqual(okk, True)

        """ check if the item to be removed is not in the cart """
        okk = self.marketplace.remove_from_cart(cr1, self.products[1])
        self.assertEqual(okk, False)

    def test_place_order(self):
        self.marketplace.publish(0, self.products[0])
        self.marketplace.publish(1, self.products[1])
        cr1 = self.marketplace.new_cart()

        self.marketplace.add_to_cart(cr1, self.products[0])
        self.marketplace.add_to_cart(cr1, self.products[1])

        """ check the ordered products from the cart """
        order = self.marketplace.place_order(0)
        self.assertEqual(self.products[0], order[0])
        self.assertEqual(self.products[1], order[1])

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        """ dictionary producer_id - [produse]"""
        self.products = {}
        """ dictionary cart_id - [(producerd_id), produs]"""
        self.carts = {}
        """ the most recent id of every prod/cart """
        self.id_prod = -1
        self.id_cart = -1
        """ 3 locks """
        self.lock_prod_id = Lock()
        self.lock_cart_id = Lock()
        self.lock_products = Lock()

        """ logger """
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.INFO)

        handler = RotatingFileHandler("marketplace.log", maxBytes=2000, backupCount=10)

        formatter = logging.Formatter("%(asctime)s; %(message)s", "%Y-%m-%d %H:%M:%S")
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)


    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.logger.info('Register_producer input: N/A')
        self.lock_prod_id.acquire()
        self.id_prod += 1

        result = self.id_prod
        self.lock_prod_id.release()

        self.logger.info('Register_producer output: ' + str(self.id_prod))
        return result

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info("Publish input:" + str(producer_id) + " AND " + str(product))

        """ if the producer uses this market """
        if producer_id in self.products.keys():

            """ if the market has enough room for another product """
            if len(self.products[producer_id]) < self.queue_size_per_producer:

                """ lock the list which is going to be modified"""
                self.lock_products.acquire()
                self.products[producer_id].append(product)
                self.lock_products.release()

                self.logger.info("Publish output: True")
                return True

        else:
            """ the producer is not registered yet"""
            self.products[producer_id] = [product]
            self.logger.info("Publish output: True")
            return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.logger.info("New_cart input: N/A")
        self.lock_cart_id.acquire()

        self.id_cart += 1
        result = self.id_cart
        self.carts[self.id_cart] = []

        self.lock_cart_id.release()

        self.logger.info("New_cart output: " + str(self.id_cart))
        return result

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.logger.info("Add_to_cart input: " + str(cart_id) + " AND " + str(product))

        """ if the cart is not yet registered """
        if cart_id > self.id_cart:
            self.logger.info("Add_to_cart output: False")
            return False

        for prod_id in self.products.keys():
            """ found the wanted product """
            if product in self.products[prod_id]:

                self.lock_products.acquire()
                """ add the wanted prod to the cart """
                elem = (prod_id, product)
                self.carts[cart_id].append(elem)

                """ eliminate it from the marketplace """
                self.products[prod_id].remove(product)
                self.lock_products.release()

                self.logger.info("Add_to_cart output: True")
                return True

        self.logger.info("Add_to_cart output: False")
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info("Remove_from_cart input:" + str(cart_id) + " AND " + str(product))

        """ the cart is not registered """
        if cart_id > self.id_cart:
            self.logger.info("Remove_from_cart output: False")
            return False

        for elem in self.carts[cart_id]:
            prod = elem[1]
            prod_id = elem[0]

            """ found the cart with the wanted product """
            if prod == product:
                self.lock_products.acquire()

                """ remove from cart """
                self.carts[cart_id].remove(elem)
                """ add to the market """
                self.products[prod_id].append(prod)

                self.lock_products.release()
                self.logger.info("Remove_from_cart output: True")
                return True
        self.logger.info("Remove_from_cart output: False")
        return False


    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info("Place_order input: card_id = " + str(cart_id))

        prod_list = []

        """ add every product from the cart """
        for elem in self.carts[cart_id]:
            prod = elem[1]
            prod_list.append(prod)

        """ delete the cart """
        del self.carts[cart_id]

        self.logger.info("Place_order output:" + str(prod_list))
        return prod_list
