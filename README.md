
# Toxicity Analysis

## Overview
The **Toxicity Analysis** project is designed to analyze the toxicity of content collected from Reddit and 4chan. This project uses **ModerateHateSpeech API** to analyze the toxicity levels of text in posts and comments. Toxicity is categorized into two classes: **flag** (high toxicity) and **normal** (normal toxicity), with confidence scores representing the certainty of the classification. The results are stored in a MongoDB database for further analysis.

## Data Collection

### 1. Reddit Data Collection
The data is collected from various political subreddits using the **Reddit API**. You can find the relevant repository for collecting Reddit data here:  
[Reddit Crawler Repository](https://github.com/hanushgowrav66/redditCrawler)

The Reddit data collection works as follows:
- Posts and comments are collected from specific subreddits such as `r/politics`, `r/uselection`, etc.
- The content is stored in MongoDB collections, and a toxicity analysis is performed on each piece of text in the posts and comments.

### 2. 4chan Data Collection
The 4chan data is collected from different boards using the **4chan API**. You can find the relevant repository for collecting 4chan data here:  
[4chan Crawler Repository](https://github.com/hanushgowrav66/4chanCrawler)

The 4chan data collection works as follows:
- Threads are scraped from specific boards such as `pol` and `news`.
- The content from posts in these threads is stored in MongoDB collections, and toxicity analysis is applied to each post.

## Toxicity Analysis
Toxicity is analyzed using the **ModerateHateSpeech API**. The API response returns the toxicity classification (`flag` or `normal`) along with a confidence score between `0` and `0.99`.

- **`toxicity`**: Contains the class (`flag` or `normal`) and the confidence score.
  
Example:
```json
{
  "toxicity": {
    "class": "flag",
    "confidence": 0.95
  }
}
```

### What Happens During Toxicity Analysis:
1. The content (text) from posts and comments is sent to the **ModerateHateSpeech API** for toxicity classification.
2. The returned data includes a **class** (`flag` for high toxicity and `normal` for normal content) and a **confidence score** indicating how confident the API is in its classification.
3. The results are added as a new field called `toxicity` in the database, and the content is marked with its respective toxicity classification.

---

## How to Run the Project

### Requirements:
- Python 3.x
- MongoDB running locally
- **ModerateHateSpeech API** key

### Setup:
1. Clone the repository and install dependencies:
   ```bash
   git clone <repo_url>
   cd <repo_folder>
   pip install -r requirements.txt
   ```

2. Add your **ModerateHateSpeech API key** to the environment variable or directly in the code:
   ```python
   API_KEY = "add-your-api-key"
   ```

3. Start MongoDB on your local machine.

4. Run the script to begin collecting data and analyzing toxicity:
   ```bash
   python toxicity_analysis.py
   ```

---

## Notes
- The data collection scripts for Reddit and 4chan are independent, and you need to run both to populate the MongoDB database.
- The script processes the data in batches, fetching posts and comments, analyzing toxicity, and updating the database accordingly.
- The project uses multiprocessing and threading for efficient data processing.

---
