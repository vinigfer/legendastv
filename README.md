Installation:
---------

```
pip install legendastv
```

How to use:
---------

```
from legendastv import LegendasTV
legendas_tv = LegendasTV('your_login', 'your_password')
legendas_tv.search('The Big Bang Theory', 'S12E18')
url = legendas_tv.search('The Big Bang Theory', 'S12E18')
legendas_tv.download(url, '/destination/folder/file_name')
```

Can you contribute? Sure! Open a Pull Request, but don't forget to:
---------
- Apply PEP8 (120 characters limit)
- Apply Black  (120 characters limit)
- Apply isort

What is missing:
---------
- Tests
- Coverage / badges
- Add MyPy annotations
