import time

def get_hour():
    try:
        t = time.localtime()
        return t.tm_hour
    except:
        # Fallback if time not set
        return 12