#!/usr/bin/env python3
# Copyright (c) 2017-2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""An example functional test

The module-level docstring should include a high-level description of
what the test is doing. It's the first thing people see when they open
the file and should give the reader information about *what* the test
is testing and *how* it's being tested
"""
# Imports should be in PEP8 ordering (std library first, then third party
# libraries then local imports).
from collections import defaultdict

# Avoid wildcard * imports
# Use lexicographically sorted multi-line imports
from test_framework.blocktools import (
    create_block,
    create_coinbase,
)
from test_framework.messages import (
    CInv,
    MSG_BLOCK,
)
from test_framework.p2p import (
    P2PInterface,
    msg_block,
    msg_getdata,
    p2p_lock,
)
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
)

# P2PInterface is a class containing callbacks to be executed when a P2P
# message is received from the node-under-test. Subclass P2PInterface and
# override the on_*() methods if you need custom behaviour.
class BaseNode(P2PInterface):
    def __init__(self):
        """Initialize the P2PInterface

        Used to initialize custom properties for the Node that aren't
        included by default in the base class. Be aware that the P2PInterface
        base class already stores a counter for each P2P message type and the
        last received message of each type, which should be sufficient for the
        needs of most tests.

        Call super().__init__() first for standard initialization and then
        initialize custom properties."""
        super().__init__()
        # Stores a dictionary of all blocks received
        self.block_receive_map = defaultdict(int)

    def on_block(self, message):
        """Override the standard on_block callback

        Store the hash of a received block in the dictionary."""
        message.block.calc_sha256()
        self.block_receive_map[message.block.sha256] += 1

    def on_inv(self, message):
        """Override the standard on_inv callback"""
        pass

def custom_function():
    """Do some custom behaviour

    If this function is more generally useful for other tests, consider
    moving it to a module in test_framework."""
    # self.log.info("running custom_function")  # Oops! Can't run self.log outside the BitcoinTestFramework
    pass


class ExampleTest(BitcoinTestFramework):
    # Each functional test is a subclass of the BitcoinTestFramework class.

    # Override the set_test_params(), skip_test_if_missing_module(), add_options(), setup_chain(), setup_network()
    # and setup_nodes() methods to customize the test setup as required.

    

    def set_test_params(self):
        """Override test parameters for your individual test.

        This method must be overridden and num_nodes must be explicitly set."""
        # By default every test loads a pre-mined chain of 200 blocks from cache.
        # Set setup_clean_chain to True to skip this and start from the Genesis
        # block.
        self.setup_clean_chain = True
        self.num_nodes = 3
        # Use self.extra_args to change command-line arguments for the nodes
        self.extra_args = [[], ["-logips"], []]

        # self.log.info("I've finished set_test_params")  # Oops! Can't run self.log before run_test()

    # Use skip_test_if_missing_module() to skip the test if your test requires certain modules to be present.
    # This test uses generate which requires wallet to be compiled
    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    # Use add_options() to add specific command-line options for your test.
    # In practice this is not used very much, since the tests are mostly written
    # to be run in automated environments without command-line options.
    # def add_options()
    #     pass

    # Use setup_chain() to customize the node data directories. In practice
    # this is not used very much since the default behaviour is almost always
    # fine
    # def setup_chain():
    #     pass

    def setup_network(self):
        """Setup the test network topology

        Often you won't need to override this, since the standard network topology
        (linear: node0 <-> node1 <-> node2 <-> ...) is fine for most tests.

        If you do override this method, remember to start the nodes, assign
        them to self.nodes, connect them and then sync."""

        self.setup_nodes()

        # In this test, we're not connecting node2 to node0 or node1. Calls to
        # sync_all() should not include node2, since we're not expecting it to
        # sync.
        self.connect_nodes(1, 2)
        self.sync_all(self.nodes[0:2])

    # Use setup_nodes() to customize the node start behaviour (for example if
    # you don't want to start all nodes at the start of the test).
    # def setup_nodes():
    #     pass



    def run_test(self):
        """Main test logic"""

        # Create P2P connections will wait for a verack to make sure the connection is fully up
        peer_messaging = self.nodes[1].add_p2p_connection(BaseNode())
        
        self.log.info("node 1 height is")
        self.log.info(self.nodes[1].getblockcount())
        self.log.info("node 2 height is")
        self.log.info(self.nodes[2].getblockcount())


        # Generating a block on one of the nodes will get us out of IBD
        blocks = [int(self.generate(self.nodes[1], sync_fun=lambda: self.sync_all(self.nodes[1:2]), nblocks=2)[0], 16)]
        
        self.log.info("node 1 height is")
        self.log.info(self.nodes[1].getblockcount())
        self.log.info("node 2 height is")
        self.log.info(self.nodes[2].getblockcount())



if __name__ == '__main__':
    ExampleTest().main()
