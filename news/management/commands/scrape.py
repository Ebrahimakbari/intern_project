from django.core.management.base import BaseCommand
from news.scraper import ZoomitScraper



class Command(BaseCommand):
    help = 'Scrape news from Zoomit.ir'

    def handle(self, *args, **options):
        scraper = ZoomitScraper()
        scraper.scrape_archive()