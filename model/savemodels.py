import joblib

def save_model(model, idx, models_name):
    name = f'trained_model/{models_name[idx]}.pkl'
    joblib.dump(model, name)
        

  

    