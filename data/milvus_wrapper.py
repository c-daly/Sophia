from pymilvus import Milvus, DataType, IndexType, CollectionSchema, FieldSchema
from pymilvus import Collection
class MilvusWrapper:
    def __init__(self, host='standalone', port='19530'):
        self.client = Milvus(host=host, port=port)
        self.create_collection('sophia')

    def create_collection(self, collection_name, dimension=1536):
        # Define collection schema
        #collection_schema = CollectionSchema(
        #    fields=[
        #        FieldSchema(name='id', dtype=DataType.INT64, description="ID", is_primary=True),
        #        FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=dimension, description="Vector")
        #    ]
        #)
        collection_schema = {
            "fields": [
                {
                    "name": "embedding",
                    "type": DataType.FLOAT_VECTOR,
                    #"metric_type": MetricType.L2,
                    "metric_type": "L2",
                    "params": {"dim": dimension},
                    "indexes": [{"type": IndexType.FLAT}]
                },
                {
                    "name": "id",
                    "type": DataType.INT64,
                    "is_primary": True,
                    "auto_id": True
                }
            ],
            "segment_row_limit": 4096
        }
        if not self.client.has_collection(collection_name):
            self.client.create_collection(collection_name, schema=collection_schema)
        self.client.load_collection(collection_name)

    def insert_vector(self, collection_name, vector, id):
        # Insert the vector into the collection
        record = {
            "id": id,
            "embedding": vector,
        }

        try:
            return self.client.insert(collection_name, records=[record])
        except Exception as e:
            print(e)
    def insert_vectors(self, collection_name, vectors):
        # Insert the vectors into the collection
        #return self.client.insert(collection_name, records=vectors, field_name="embedding")
        return self.client.insert(collection_name, records=vectors)

    def search_vectors(self, query_vector, top_k=10):
        collection_name = "sophia"
        # Search for similar vectors in the collection
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.client.search(collection_name, [query_vector], "embedding", param=search_params, limit=top_k) #, index_param=index_param)
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
