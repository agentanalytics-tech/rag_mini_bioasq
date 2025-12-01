import os
import pandas as pd
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()  # This loads the .env file

# ========================================================================
# STEP 1 — MERGE QA TRAIN + TEST INTO ONE CSV (MODIFIED)
# ========================================================================
print("\n📌 Loading QA dataset...")

qa = load_dataset("enelpol/rag-mini-bioasq", "question-answer-passages")

df_train = qa["train"].to_pandas()
df_test = qa["test"].to_pandas()

df_all = pd.concat([df_train, df_test], ignore_index=True)
df_all = df_all[["question", "answer", "id", "relevant_passage_ids"]]

df_all['relevant_passage_ids'] = df_all['relevant_passage_ids'].apply(lambda x: ",".join(map(str, x)))

rename_dict = {
    "id": "id",
    "relevant_passage_ids": "doc_ids",  # This column now holds comma-separated strings
    "question":"question"
}
df_all.rename(columns=rename_dict, inplace=True)

DATA_DIR_SOURCE=os.getenv("DATA_DIR_SOURCE")
print(DATA_DIR_SOURCE)
os.makedirs(DATA_DIR_SOURCE, exist_ok=True) 
QUERY_MAP_SOURCE_FILE=os.getenv("QUERY_MAP_SOURCE_FILE")
csv_path = f"{DATA_DIR_SOURCE}/{QUERY_MAP_SOURCE_FILE}"
df_all.to_csv(csv_path, index=False)

print(f"✅ Saved merged QA file → {csv_path}")


# ========================================================================
# STEP 2 — SAVE CORPUS PASSAGES AS TEXT FILES
# ========================================================================
print("\n📌 Loading complete corpus dataset (corpus['test'])...")
corpus = load_dataset("enelpol/rag-mini-bioasq", "text-corpus")["test"]
DATA_DIR_TARGET=os.getenv("DATA_DIR_TARGET")
os.makedirs(DATA_DIR_TARGET, exist_ok=True)
print(f"📁 Saving passages to → {DATA_DIR_TARGET}\n")
for idx, item in enumerate(corpus):
    pid = str(item["id"])
    text = item["passage"]
    filepath = os.path.join(DATA_DIR_TARGET, f"{pid}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    if idx % 500 == 0:
        print(f"... saved {idx}/{len(corpus)} passages")

print("\n🎉 DONE — RAG evaluation data is ready!")
print(f"➡ QA CSV    : {csv_path}")
print(f"➡ Passage TXT: {os.path.abspath(DATA_DIR_TARGET)}")