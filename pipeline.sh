echo "Converting json to csv"
python json2csv.py

echo "Data Preprocessing..."
python data_prep.py

echo "Model Training"
python model/NN_model/train.py
python model/ml_train.py