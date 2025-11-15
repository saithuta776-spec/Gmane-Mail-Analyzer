📨 Gmane Mail Analyzer

A full end-to-end Python project that retrieves public GMane email archives, parses and indexes metadata, extracts keywords from subject lines, and visualizes the results in an interactive D3.js word cloud.

This project demonstrates:
	•	📥 Fetching email data from a public GMane archive
	•	🧹 Parsing, cleaning, and normalizing email metadata
	•	🗄️ Building structured SQLite databases
	•	🧠 Keyword extraction & frequency analysis
	•	🧪 Auto-generating gword.js for visualization
	•	🌈 A fully interactive HTML / D3.js word cloud



📁 Project Structure

```txt

├── src/                                     # Core Python scripts
│   ├── fetch_emails.py                      # Fetch raw emails → content.sqlite
│   ├── prepare_index.py                     # Clean & normalize → index.sqlite
│   ├── generate_wordcloud_js.py             # Build final gword.js dataset
│   └── gbasic.py                            # Shared helpers/utilities
│
├── visualization/
│   ├── wordcloud.html                       # Interactive D3 visualization
│   └── gword.js                             # Keyword dataset (auto-generated)
│
├── data/                                    # SQLite databases
│   ├── content.sqlite
│   └── index.sqlite
│
├── .gitignore
└── README.md

```






🚀 How to Run the Project

```txt

Follow these steps to reproduce the full pipeline from email retrieval → database indexing → visualization.

1️⃣ Create and activate a virtual environment

python3 -m venv .venv
source .venv/bin/activate

Install required packages:
	pip install python-dateutil


2️⃣ Fetch Emails (Raw Data → content.sqlite)

This script downloads email headers + body text from the GMane public archive and stores them inside data/content.sqlite.
	python src/fetch_emails.py

You will be prompted with:
	How many link :
	Enter how many messages you want to fetch (e.g., 20, 50, 100, etc.).

✔ Output database:
	data/content.sqlite

3️⃣ Build the Indexed Database (content → index)

This step:
	•	Normalizes email addresses
	•	Extracts message IDs, subjects, timestamps
	•	Cleans sender domains
	•	Compresses headers & bodies
	•	Produces a structured relational database

Run:
	python src/prepare_index.py

✔ Output database:
	data/index.sqlite


4️⃣ Generate the Word Cloud Dataset (index.sqlite → gword.js)

This step extracts the top 100 keywords from subject lines and builds a JavaScript dataset.

Run:
	python src/generate_wordcloud_js.py

✔ Output file:
	visualization/gword.js

5️⃣ Open the Interactive Visualization

Simply open this file in a browser:

	visualization/wordcloud.html

✔ A D3.js word cloud will appear
✔ You can click any keyword to inspect its frequency-based size
```





🛠 Project Workflow Overview

This is the entire pipeline your project performs—from downloading raw data to visualizing insights.

```txt

📥 Step 1: Retrieve Emails
	•	Download raw mbox emails from GMane (public web archive)
	•	Store each email’s header + body
	•	Save into content.sqlite

Output: Raw, unprocessed email data



🧹 Step 2: Parse + Normalize
	•	Clean sender addresses (domain normalization)
	•	Extract:
	•	Sender
	•	Subject
	•	Date
	•	Message-ID
	•	Convert dates into consistent ISO format
	•	Prepare the relational index

Output: index.sqlite (cleaned + searchable)



🧠 Step 3: Keyword Extraction
	•	Read all subject lines
	•	Remove punctuation/numbers
	•	Break into words
	•	Ignore words < 4 characters
	•	Count frequency
	•	Rank highest → lowest



Output: Python dictionary of keyword counts
🧪 Step 4: Generate JavaScript Dataset
	•	Convert frequencies into size weights (20px–100px)
	•	Write the final D3-readable file:
		visualization/gword.js



Output: JSON-like JS array used by the word cloud
🌈 Step 5: Interactive Visualization
	•	D3.js cloud layout positions the words
	•	Colors, rotations, sizes applied dynamically
	•	Users can click words to inspect size

Output:
A fully interactive word cloud visualizing keyword importance.


```



📜 License

```txt

MIT License

Copyright (c) 2025 Sai Thuta

Permission is hereby granted, free of charge, to any person obtaining a copy…

```


🙌 Acknowledgements
```txt
	•	Based on concepts from Python For Everbody (University of Michigan) (Coursera)
	•	GMane public mail archive for open data
	•	Credtit to course instructor Dr. Chuck (Charles Severance)
	•	Project refactored and implemented by Sai Thuta Hlaing (Cairney)

```




