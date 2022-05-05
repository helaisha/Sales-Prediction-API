
This project is a prediction api for GBNL making use of the flask. 
Follow the instructions below to run locally on your system .

Start virtual environment 
```bash
 source venv/bin/activate   
```

Install requirements
```bash
pip install -r requirements.txt
```
## Starting the App

```bash
python app.py
```

The format to call the APIs with examples is given below :


```bash
http://127.0.0.1:5000/predict/region?location=depot&sku=item_no&month=month
```

```bash

http://127.0.0.1:5000/predict/lg?location=AGEGE&sku=10040447&month=11


http://127.0.0.1:5000/predict/sw?location=OKENE&sku=10040447&month=1


http://127.0.0.1:5000/predict/se?location=ABA&sku=10056877&month=11



http://127.0.0.1:5000/predict/mb?location=BAUCHI&sku=108880&month=3



http://127.0.0.1:5000/predict/nt?location=KATSINA&sku=10040447&month=4

```


To training manually run 
```bash
http://127.0.0.1:5000/training/region 
```
e.g 
```bash
http://127.0.0.1:5000/training/lg
```

Run the code below to build and run on docker

```bash
 docker build --tag prediction-api .
```

```bash
 docker run -it -p 5000:5000 prediction-api .
 
```