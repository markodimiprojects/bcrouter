# bcRouter
This repository stores the implementation utilized for my bachelor thesis.

It contains most elements required to get the project running.

# Prerequisites

Before starting the project, two programs must be installed beforehand.

### Docker Desktop  v4.27.2
This project utilizes Docker to set up an almost complete project structure.
Similar versions to this Docker version should be compatible.

### Ganache v2.7.1
Ganache is utilized to set up a local accessible blockchain .
This implementation requires a Ethereum testchain.
Further information regarding the configuration follows below.
# Setup
The main program requires environment variables to work.
Add these variables:

1. NODE_URL_TEST: URL to the blockchain connection (Default: Ganache - localhost:7545)
2. CONTRACT_ADDRESS_TEST: Address reference to the created smart contract
3. CALLER_TEST: Address of the blockchain connection
4. PRIVATE_KEY_TEST: Private key of the blockchain connection (Must be used to alter the blockchain)
5. HTTPURL_TEST: HTTP endpoint of Routinator (Default: localhost:8323)


For CONTRACT_ADDRESS_TEST create the smart contract beforehand using a third party, like Remix for example.

Once that is finished, use "docker-compose up --build" to start the project.
By default, the program will upload the base snapshot and all new deltas in parallel.
To change that, adjust the main function call in main.py.
# Notes
* **_Contact:_** For more detailed information, please refer to the bachelor thesis or contact me via email at s4832179@stud.uni-frankfurt.de
* **_Feedback and Contributions:_** Feedback, suggestions, and contributions are highly appreciated as this is a proof of concept! 
If you have any ideas for improvements or would like to contribute enhancements, please submit a pull request or open an issue on GitHub.