from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re  # Import regex for extracting votes & title cleanup

# Set up Selenium WebDriver
driver = webdriver.Chrome()

# IMDb URL (Modify based on the exact listing page)
url = "https://www.imdb.com/search/title/?year=2024"
driver.get(url)

# Wait for the page to load
time.sleep(5)

# Find all movie containers
movie_containers = driver.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item")

# Initialize empty list to store movie data
movies_data = []

# Loop through each movie container and extract details
for movie in movie_containers[:50]:  # Extract details for the first 50 movies
    try:
        # Extract Title and remove numbering (e.g., "1. The Brutalist" → "The Brutalist")
        title_raw = movie.find_element(By.CSS_SELECTOR, "h3.ipc-title__text").text.strip()
        title = re.sub(r"^\d+\.\s*", "", title_raw)  # Remove leading "1. " from title

        # Extract Year, Duration, Age Rating
        metadata = movie.find_elements(By.CLASS_NAME, "dli-title-metadata-item")
        year = metadata[0].text if len(metadata) > 0 else "N/A"
        duration = metadata[1].text if len(metadata) > 1 else "N/A"
        age_rating = metadata[2].text if len(metadata) > 2 else "N/A"

        # Try extracting IMDb Rating & Votes safely
        try:
            rating_element = movie.find_elements(By.CLASS_NAME, "ipc-rating-star")
            if rating_element:
                rating_text = rating_element[0].text.strip()  # Example: "7.6\n(58K) Rate"
                rating_match = re.search(r"(\d+\.\d+)", rating_text)  # Extract number like 7.6
                votes_match = re.search(r"\((.*?)\)", rating_text)  # Extract text inside ()

                imdb_rating = rating_match.group(1) if rating_match else "N/A"
                votes = votes_match.group(1) if votes_match else "N/A"
            else:
                imdb_rating = "N/A"
                votes = "N/A"
        except:
            imdb_rating = "N/A"
            votes = "N/A"

        # Append data to list
        movies_data.append({
            "Title": title,
            "Year": year,
            "Duration": duration,
            "Age Rating": age_rating,
            "IMDb Rating": imdb_rating,
            "Votes": votes
        })
    
    except Exception as e:
        print(f"Skipping a movie due to error: {e}")

# Convert to Pandas DataFrame
df = pd.DataFrame(movies_data)

# Save to CSV
df.to_csv("IMDb_2024_Movies.csv", index=False)

# Close the WebDriver
driver.quit()

# Display the DataFrame
print(df.head())
