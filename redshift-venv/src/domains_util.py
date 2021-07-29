from bs4 import BeautifulSoup
import requests

from decimal import Decimal


def get_title(domain_tasks, titles):
    """Scrapes webpages for title tag text until domain_tasks queue is empty

    Args:
        domain_tasks (Queue): Thread safe queue to allow multiple concurrent processing of scraping
        titles (list of str): List of page titles indexed based on thread task to be returned by API

    Returns:
        bool: Whether scraping succeeded or failed
    """
    while not domain_tasks.empty():
        domain = domain_tasks.get()

        try:
            page = requests.get(domain[1])
        except requests.exceptions.MissingSchema as err:
            titles[domain[0]] = "Invalid URL " + domain[1]
        except requests.exceptions.ConnectionError as err:
            titles[domain[0]] = "Could not connect to " + domain[1]
        else:
            # Scrape page for title tag and store in results with task id to prevent
            # threads clashing
            soup = BeautifulSoup(page.content, features="html.parser")
            titles[domain[0]] = soup.find('title').string

        domain_tasks.task_done()


def update_time(time_taken, TimeTracker):
    """Stores total execution time and number of API calls to date in mongodb

    Args:
        time_taken (int): time in seconds for the request to execute up until this point
    """
    api_tracker = TimeTracker.objects().first()
    if not api_tracker:
        # Initialize api_tracker if none exists
        initial_tracker = TimeTracker(total_invocations=1, total_time=time_taken)
        initial_tracker.save()
        return

    total_invocations = api_tracker.total_invocations + 1
    total_time = api_tracker.total_time + Decimal(time_taken)

    api_tracker.update(total_invocations=total_invocations, total_time=total_time)