# WiBIT - Virtual Tourist Information Office

### Local run

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
In order to run you need to move to `/app` directory:
```
cd app
```
And then run it using:
```
python3 app.py
```
If you want to stop app just use `Ctrl + C`

### Deployment

For deployment, there was `app/passenger_wsgi.py` file prepared.

### Tensorflow model problem
After downloading repository from git, there could be some problems with using `app/chatbot/models/tfidf_bigger_nn` model.
It can be necessary to prepare this model once again and replace it in `app/chatbot/models` directory. 
The easiest way to do it is to use `text-operations/notebooks/prepare_final_model.ipynb` notebook.
It needs some files to train the model:
- train dataset csv (`text-operations/files/oversample_stemmed_train_df.csv`) 
- test dataset csv (`text-operations/files/test_df.csv`) 
- pretrained tfidf model (`text-operations/models/tfidf_vectorizer_wibit_joblib`) 