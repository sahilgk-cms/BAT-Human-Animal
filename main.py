import subprocess
import os
import sys

current_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(current_path))
sys.path.append(root_path)

#run the scrapers
subprocess.run(["python", os.path.join("pipeline", "scrapers", "google_alerts_scraper.py")])
subprocess.run(["python", os.path.join("pipeline", "scrapers", "newsapi_scraper.py")])
subprocess.run(["python", os.path.join("pipeline", "scrapers", "serpapi_scraper.py")])

