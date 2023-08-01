class CommonCrawlQuery:
    def __init__(self, crawl, urls, url_path, fetch_status, limit):
        self.crawl = crawl
        self.urls = urls
        self.url_path = url_path
        self.fetch_status = fetch_status
        self.limit = limit
