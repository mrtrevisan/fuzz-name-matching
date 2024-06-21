## Fuzz Name matching

### Dependencies
- Python 3
- Pipenv

### How to use

1. Create a .venv dir: (pipenv will use it as project virtual env) 
```
mkdir .venv
```

2. Run pipenv install: (this will install all dependecnies)
```
pipenv install
```

3. Place your data csv in data dir, name it ```data.csv```. An example is provided, following CAPES' standard.  
Your file tree should look like this:  
```
.
+-- .venv
|    +-- ...
+-- src
|    +-- ...
+-- data
|    +-- data.csv
|    +-- ...
...
```

3. Run fuzz test. You may need to adjust the encoding parameter in source code.

```
pipenv run python3 src/fuzz_test.py
```
