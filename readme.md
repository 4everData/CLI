# Solana Storage Manager

A CLI tool for secure file storage using Solana blockchain and IPFS. This tool allows you to upload files to IPFS and store their encrypted URLs on the Solana blockchain, enabling decentralized and permanent storage with blockchain-based retrieval.

## Features

- Upload files to IPFS with automatic pinning
- Store encrypted file URLs on Solana blockchain
- Retrieve files using transaction signatures
- Chunked data storage for handling large URLs
- Built-in encryption for enhanced security

## Prerequisites

- Python 3.7+
- Solana CLI tools
- A Solana wallet with SOL for transaction fees

## Installation

```bash
# Clone the repository
git clone https://github.com/4everdata/CLI

# Install dependencies
pip install -r requirements.txt
```

## Required Dependencies

```
click
requests
solders
solana
base64
```

## Usage

### Upload a File

```bash
python storage_manager.py upload <FILE_PATH> <PRIVATE_KEY>
```

- `FILE_PATH`: Path to the file you want to upload
- `PRIVATE_KEY`: Your Solana wallet's base58-encoded private key

Example:
```bash
python storage_manager.py upload ./myfile.pdf EXAMPLEprivateKEYbase58string
```

### Download a File

```bash
python storage_manager.py download <SIGNATURE>
```

- `SIGNATURE`: Transaction signature from the upload process

Example:
```bash
python storage_manager.py download 4vC38Dgm4GKn1KZ ... 
```

## Security Features

- URL encryption using XOR cipher
- Chunked data storage for large files
- Base64 encoding for binary data
- Decentralized storage across IPFS network

## Configuration

The tool uses the following services:
- Solana Mainnet RPC endpoint
- Pinata IPFS service
- Solana Memo program

## Error Handling

The tool includes comprehensive error handling for:
- Failed uploads
- Transaction errors
- Network issues
- Invalid signatures
- Incomplete data retrieval

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool interacts with the Solana blockchain and handles cryptocurrency transactions. Always verify transactions and keep your private keys secure.
