# OnTheFlyNewsAnalyzer
## Install
```
pip install openai
pip install chaimlit
pip install tqdm
pip install datasets
```

## Dataset Preparation
We use a local copy of CCNews dataset. The first run of command below will induce downloading, filtering, and storing dataset locally. We use CCNews data in 2024 in language of EN. After downloading, the files will be stored in default to shards such as:
```
./dataset/filtered_data/train/data-00000-of-00061.arrow
...
./dataset/filtered_data/train/data-00061-of-00061.arrow
```
This will be about `31GB` on your disk.

## Running from Chainlit

Run in terminal:

```
chainlit run app.py -w
```

Follow the opened localhost webpage to begin! Notice that Chainlit occassionally fails on the web-end, but results for final answer will still be saved locally.

## Running from Terminal

Run in terminal:

```
python main.py --query YOUR QUERY --topic ANY
```
Them provide your answer directly in the terminal. Running from the terminal will also store extra information such as keywords used, Schema definition, Schema instance filled with source article index, etc.
