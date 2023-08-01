import time


class AthenaQuery:
    template = """
        SELECT warc_filename, warc_record_offset, warc_record_length
        FROM "ccindex"
        WHERE crawl = '%s'
            AND url_host_registered_domain IN (%s)
            AND url_path like '%s'
            AND fetch_status = %s
        LIMIT %s
        """

    def __init__(self, common_crawl_query):
        self.crawl = common_crawl_query.crawl
        self.urls = common_crawl_query.urls
        self.url_path = common_crawl_query.url_path
        self.fetch_status = common_crawl_query.fetch_status
        self.limit = common_crawl_query.limit

    # a function that returns a formatted query string
    def get_query_string(self):
        # wrap each url in single quotes and join with commas
        formatted_urls = ",".join(["'" + url + "'" for url in self.urls])
        # escape % in url path
        url_path_escaped = self.url_path.replace("%", "%%")
        return self.template % (
            self.crawl,
            formatted_urls,
            url_path_escaped,
            self.fetch_status,
            self.limit,
        )

    def __str__(self):
        return self.get_query_string()


class Athena:
    def __init__(self, client):
        self.client = client

    def execute_query(self, query_string, output_location):
        query_response = self.client.start_query_execution(
            QueryString=query_string,
            ResultConfiguration={"OutputLocation": output_location},
        )

        if query_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise RuntimeError("Error running query", query_response)

        query_execution_id = query_response["QueryExecutionId"]
        return query_execution_id

    def query_execution_status(self, query_execution_id):
        query_status_response = self.client.get_query_execution(
            QueryExecutionId=query_execution_id
        )

        if query_status_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise RuntimeError("Error fetching query status", query_status_response)

        query_execution_status = query_status_response["QueryExecution"]["Status"]
        return query_execution_status

    def poll_query_execution_status(self, query_execution_id):
        final_states = ["FAILED", "SUCCEEDED", "CANCELLED"]
        query_status = self.query_execution_status(query_execution_id)

        # while query status is not final states, check every 2 seconds
        while query_status["State"] not in final_states:
            query_status = self.query_execution_status(query_execution_id)
            print(query_status)
            time.sleep(2)

        return query_status
