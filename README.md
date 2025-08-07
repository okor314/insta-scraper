# Instagram Scraper

This project is a Python-based Instagram scraper that automates login, gathers public post data, profile information, and followers using `Selenium` and `selenium-wire`.

## Features

- Automated login with environment variables
- Scrapes:
  - Profile metadata
  - Public post data (type, date, caption, likes, link)
  - Followers
- Parses `GraphQL` responses directly from network traffic
- Saves results to JSON files
- Detects new posts dynamically while scrolling

## Technologies Used

- Python 3.10+
- Selenium
- selenium-wire
- Chrome WebDriver

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/your-username/instagram-scraper.git
cd instagram-scraper
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt 
```

3. **Create a `.env` file** with your Instagram credentials: 

```env
INSTA_NAME=your_instagram_username
INSTA_PASS=your_instagram_password
```

