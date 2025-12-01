import json
import csv
import os
from dotenv import load_dotenv
load_dotenv()   # This loads the .env file

# ---------- Base Path ----------
DATA_DIR_SOURCE = os.getenv("DATA_DIR_SOURCE")
SOURCE_CORPUS_FILE = os.getenv("SOURCE_CORPUS_FILE")
SOURCE_QUERIES_FILE = os.getenv("SOURCE_QUERIES_FILE")
SOURCE_QREL_FILE = os.getenv("SOURCE_QREL_FILE")
QUERY_MAP_SOURCE_FILE = os.getenv("QUERY_MAP_SOURCE_FILE")

corpus_file = os.path.join(DATA_DIR_SOURCE,SOURCE_CORPUS_FILE) 
queries_file = os.path.join(DATA_DIR_SOURCE,SOURCE_QUERIES_FILE) 
qrels_file = os.path.join(DATA_DIR_SOURCE,SOURCE_QREL_FILE) 
query_map_out = os.path.join(DATA_DIR_SOURCE,QUERY_MAP_SOURCE_FILE) 

# ---------- Step 1: Load Corpus ----------
corpus = []
id_map = {}  # track cleaned IDs

with open(corpus_file, "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line.strip())
        clean_id = doc["_id"].replace(" ", "_")  # safe ID
        id_map[doc["_id"]] = clean_id  # original -> cleaned

        record = {
            "id": clean_id,
            "title": doc.get("title", ""),
            "text": doc["text"]
        }
        corpus.append(record)

# ---------- Step 2: Load Queries ----------
queries = []
with open(queries_file, "r", encoding="utf-8") as f:
    for line in f:
        queries.append(json.loads(line.strip()))

# ---------- Step 3: Load Qrels ----------
qrel_map = {}
with open(qrels_file, "r", encoding="utf-8") as f:
    for line in f:
        qrel = json.loads(line.strip())
        qid = qrel["query-id"]
        cid = id_map.get(qrel["corpus-id"], qrel["corpus-id"])  # ensure cleaned ID
        qrel_map.setdefault(qid, []).append(cid)

# ---------- Step 4: Write Query Relevance CSV ----------
with open(query_map_out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "question", "doc_ids"])
    writer.writeheader()

    for idx, q in enumerate(queries):
        relevant = qrel_map.get(q["_id"], [])
        writer.writerow({
            "id": idx,
            "question": q["text"],
            "doc_ids": ",".join(relevant)
        })

print(f" Dataset preparation complete:\n - {query_map_out}")
