# news/tasks.py
from celery import shared_task
from .scraper import ZoomitScraper



@shared_task
def scrape_zoomit():
    """Task to scrape Zoomit website"""
    scraper = ZoomitScraper()
    scraper.scrape_archive()
    return "Zoomit scraping completed successfully"
