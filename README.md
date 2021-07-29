# domainsapi
## Quickstart
`python -m domains_api`
### /titles - POST
Scrapes webpages asynchronously and pulls there titles text

Expects Input:
  json (list of str): Contains a list of fully qualified urls of format: http(s)://<url>

  Returns:
      list of str: A list of titles from webpages from urls in domains
        
### /titles/stats - GET
Provides average request time and number of invocations of /titles

  Returns:
      dict of str: str/int : contains average time and number of times /titles has been accessed
