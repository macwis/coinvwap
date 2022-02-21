# Improvements

General:

- API endpoints documentation (although quite clear from the assignment)
- The phrase "borrowed" in terms of ABNF is not a best phrasing. The code has been reused legally based on the license. The license of the ABNF code should be explicitly noted in README.
- Not all API param combinations were thoroughly tested, this specifically includes:
  -- channel variations according to the Coinbase docs
  -- different message types, different params names
  -- various possible responses from Coinbase
  -- various possible frame-lengths and websocket protocol specifics
  -- error's handling in the data stream (e.g. invalid subscription)
- Prev. point is relevant to the code coverage. Code coverage does not have to be 100%. 100% does not guarantee anything, but proper testing should reduce the major risks of the software wrongdoing or failure. Moving towards 100% may help to uncover hidden behaviors by forcing to run all conditions.
- wherever I use an arbitrary number like 1024 indicating number of bytes to read it should be from a config or at least a constant defined.
- file names could be named from classes inside, but I used generalized approach thinking about the possible code evolution in the future.
- more abstraction in tests, there is a lot of hard coded fixtures, some of this could be wrapped with some nice names

Minor/specific:

- coinvwap:

    - default configuration variables could be in constants
    - product_ids could be packed into an object
    - signal handler should be initiated in connect() or main module to keep up with RSP
    - _switch_protocol, rename: _switch_http_to_websocket and improve it's logging

- handshake:

    - contains only ProtocolHandler what may inspire module name change ;)
    - UUID creation for each instance maybe can be taken as const
    - self.headers could be nicer with {} declaration

- vwap:

    - vwap() and vwap_formatted() could be merged, but testing

- tests:

    - test_handshake is empty - TODO implement note missing
    - test_integration - using sleep is not great, I could actively wait for a certain conditions to be reached and timeout otherwise; assertions could be cleaner
