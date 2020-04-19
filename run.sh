#!/bin/sh
curl localhost:5000/stop;
sleep 1;
/Library/Frameworks/Python.framework/Versions/3.8/bin/python3 __init__.py

# https://oauth.vk.com/authorize?client_id=7418833&redirect_uri=medvosa2.pythonanywhere.com/vka
# https://oauth.vk.com/access_token?client_id=7418833&client_secret=C1O9YsTMWNLjVVRNAaxO&redirect_uri=medvosa2.pythonanywhere.com/vka&code=<res>&redirect_uri=https://medvosa2.pythonanywhere.com&v=5.103&grant_type=client_credentials