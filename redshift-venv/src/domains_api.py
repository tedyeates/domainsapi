from flask import request, Flask, session, jsonify
from flask_mongoengine import MongoEngine

from datetime import timedelta
import time

from queue import Queue
from threading import Thread

from domains_util import get_title, update_time


app = Flask(__name__)
app.secret_key = 'ymdDsglm5fKby7MlilNo'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(seconds=10)

app.config['MONGODB_SETTINGS'] = {
    'db': 'domainsdb',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine(app)

class APITimeTracker(db.Document):
    total_invocations = db.IntField()
    total_time = db.DecimalField()


@app.route('/titles', methods=['POST'])
def titles():
    """Scrapes webpages asynchronously and pulls there titles text

    POST Args:
        json (list of str): Contains a list of urls

    Returns:
        list of str: A list of titles from webpages from urls in domains
    """
    session.permanent = True

    domains = request.get_json()
    if not isinstance(domains, list):
        return {"error":"Expected list, recieved " + type(domains).__name__}, 400
    if len(domains) < 1:
        return {"error":"Empty List"}, 400

    # Start time tracking    
    time_start = time.perf_counter()
    
    domain_tasks = Queue(maxsize=0)
    titles = ['' for domain in domains]
    number_threads = min(100, len(domains))

    # Initialize tasks for thread queue
    for index, domain in enumerate(domains):
        domain_tasks.put((index, domain))

    # Scrape webpages with threads
    for index in range(number_threads):
        thread = Thread(target=get_title, args=(domain_tasks, titles))
        thread.start()

    domain_tasks.join()

    # End time tracking
    time_taken = time.perf_counter() - time_start
    update_time(time_taken, APITimeTracker)

    return jsonify(titles=titles), 200


@app.route('/titles/stats', methods=['GET'])
def stats():
    """[summary]

    Returns:
        [type]: [description]
    """
    api_tracker = APITimeTracker.objects().first()
    average_time = str(api_tracker.total_time / api_tracker.total_invocations)

    return {
        'total_invocations': api_tracker.total_invocations, 
        'average_time': average_time
    }, 200

if __name__ == "__main__":
    app.run()