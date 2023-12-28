# THIS BRANCH IS ONLY FOR TEST DEPLOYMENT, IT DOESN'T HAVE SOME CRUICIAL FUNCTIONALITY (EG. TENSORFLOW MODEL) BUT LOOKS GOOD

To run this app manually it is recommended to prepare virtual environment and install all recommended packages.

Python 3.10.12 was used while this page was prepared.

To install virtual environment library type:
```
pip install virtualenv
```
Then you can create venv (instead of wibit-venv you can use any name you want):
```
python -m venv wibit-venv
```
Activate venv (on Linux):
```
source venv/wibit-bin/activate
```
And then install all requirements specified in requirements.txt file:
```
pip install -r reqirements.txt
```
For NER it is also necessary to download one of spacy models:
```
python -m spacy download pl_core_news_md
```
In order to run you need to move to app directory:
```
cd app
```
And then run it using:
```
python3 app.py
```
If you want to stop app just use `Ctrl + C`
