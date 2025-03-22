# Apple Report Parser

## Overview
This script processes Apple transaction reports in TXT format and generates a single CSV file with aggregated revenue per game and currency.

## 📂 Folder Structure
```
./
├── data/
│   ├── input/                      
│   │   ├── FD_mock_0125.txt
│   │   ├── FD_mock_0225.txt
│   │   └── FD_mock_0325.txt
│   └── output/
│       └── combined_output.txt
├── scripts/
│   ├── config.py
│   └── parser.py
├── main.py
└── README.md
```

## Usage
1. **Optional: Place Apple reports (`.txt` files) inside** `data/input/`.
2. **Optional: Adjust `config.py` inside** `scripts/`  **depending on your Apple Identifiers inside** 
3. **Run the script**:
   ```sh
   python3 main.py