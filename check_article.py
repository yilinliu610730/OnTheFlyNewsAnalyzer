from datasets import load_dataset
DATA_PATH = "./dataset/filtered_data"
dataset = load_dataset(DATA_PATH)['train']


indices_wanted = [8476]


for i in indices_wanted:
    print(dataset[i])