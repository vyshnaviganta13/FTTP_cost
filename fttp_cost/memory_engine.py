import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection("fttp_history")

def save_project(site, cost):

    collection.add(
        documents=[str(cost)],
        ids=[site]
    )

def get_similar(site):

    res = collection.query(
        query_texts=[site],
        n_results=2
    )

    return res