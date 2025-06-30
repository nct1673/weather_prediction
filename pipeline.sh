echo "Converting json to csv"
python json2csv.py

echo

echo "Data Preprocessing..."
python data_prep.py

echo

echo "Model Training"
# python model/NN_model/train.py
python model/ml_train.py

# python inference/inf_dataprep.py
echo "Ready for inferencing."