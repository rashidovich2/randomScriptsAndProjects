import socks
import json
import pickle

def get_type(type_str):
    type_str = type_str.lower()
    if type_str== "socks5":
        return socks.SOCKS5
    elif type_str == "socks4":
        return socks.SOCKS4
    elif type_str == "http":
        return socks.HTTP
    else:
        raise ValueError("Proxy type not recognized")

def get_type(type_str):
    type_str = type_str.lower()
    if type_str== "socks5":
        return socks.SOCKS5
    elif type_str == "socks4":
        return socks.SOCKS4
    elif type_str == "http":
        return socks.HTTP
    else:
        raise ValueError("Proxy type not recognized")

def create_proxy(type_str, host, port, user="", password=""):
    if user and password:
        return (
            get_type(type_str),
            host,
            port,
            True,
            user,
            password
        )
    return (
        get_type(type_str),
        host,
        port
    )

def get_session_proxy(session):
    if proxies := get_proxies():
        for proxy in proxies:
            if proxy["session"] == session:
                return proxy["proxy"]
    return None

def get_proxies():
    try:
        return pickle.load(open('session.pkl', "rb"))
    except:
        return []

def save_session_proxy(session, proxy):
    proxies = get_proxies()
    data = {
        "session": session,
        "proxy": proxy
    }
    proxies.append(data)
    pickle.dump(proxies,open('session.pkl',"wb"))
        