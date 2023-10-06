from pymilvus import Milvus, DataType, IndexType, CollectionSchema, FieldSchema, connections, Collection, utility
class MilvusWrapper:
    def __init__(self, host='standalone', port='19530', collection_name='sophia'):
        connections.connect(host=host, port=port)
        self.collection_name = collection_name
        if not utility.has_collection(self.collection_name):
            self.collection = self.create_collection()
        else:
            self.collection = Collection(self.collection_name)
        self.collection.load()

    def create_collection(self, dimension=1536):
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
                FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dimension)
            ]

            schema = CollectionSchema(fields, "Sophia's embeddings database")

            collection = Collection(self.collection_name, schema)

            if not collection.indexes:
                index = {
                    "index_type": "IVF_FLAT",
                    "metric_type": "L2",
                    "params": {"nlist": 128},
                }

                collection.create_index("embeddings", index)
            return collection
            #    self.client.create_collection(collection_name, fields=[embedding_id, embedding])

    def insert_vector(self, vector, id):
        # Insert the vector into the collection
        record = {
            "id": id,
            "embeddings": vector,
        }

        try:
            return self.collection.insert([record])
        except Exception as e:
            print(f"Milvus exception: {e}")
    def insert_vectors(self, vectors):
        # Insert the vectors into the collection
        #return self.client.insert(collection_name, records=vectors, field_name="embedding")
        #return self.client.insert(collection_name, records=vectors)
        return self.client.insert(self.collection_name, records=vectors)

    def search_vectors(self, query_vector, top_k=10):
        #collection_name = "sophia_embeddings"
        try:
            # Search for similar vectors in the collection
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = self.collection.search([query_vector], "embeddings", param=search_params, limit=top_k) #, index_param=index_param)
        except Exception as e:
            print(f"Milvus search exception: {e}")
        return results

    def delete_vectors(self, collection_name, ids):
        # Delete vectors by their IDs
        self.client.delete_entity_by_id(collection_name, ids)

    def drop_collection(self, collection_name):
        # Drop the entire collection
        self.client.drop_collection(collection_name)

# Usage:
#milvus_wrapper = MilvusWrapper()
#milvus_wrapper.create_collection('my_collection')
#ids = milvus_wrapper.insert_vectors('my_collection', [[1.0]*768, [2.0]*768])
#print(milvus_wrapper.search_vectors('my_collection', [1.0]*768))
#milvus_wrapper.delete_vectors('my_collection', ids)
