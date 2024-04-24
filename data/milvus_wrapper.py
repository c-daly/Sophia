import config
from pymilvus import Milvus, DataType, IndexType, CollectionSchema, FieldSchema, connections, Collection, utility
class MilvusWrapper:
    # This connection needs to be made lazy
    def __init__(self, host='standalone', port='19530', collection_name='sophia'):
        self.connected = False
        self.collection_name = collection_name
        self.collection = None
        self.port = port
        self.host = host

    def make_connection(self):
        connections.connect(host=self.host, port=self.port)
        if not utility.has_collection(self.collection_name):
            self.collection = self.create_collection()
        else:
            self.collection = Collection(self.collection_name)
        self.collection.load()
        self.connected = True
        config.logger.debug(f"collection description: {self.collection.num_entities}")
    def create_collection(self, dimension=1536):
        config.logger.debug(f"Creating collection {self.collection_name}")
        #if not self.connected:
        #    self.make_connection()
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
        config.logger.debug(f"Inserting vector with ID {id} into collection {self.collection_name}")
        if not self.connected:
            self.make_connection()
        # Insert the vector into the collection
        record = {
            "id": id,
            "embeddings": vector,
        }

        try:
            result = self.collection.insert([record])
            self.collection.flush()
            #config.logger.debug(f"Insert result: {result}")
            return result
        except Exception as e:
            config.logger.debug(f"Milvus exception: {e}")
    def insert_vectors(self, vectors):
        if not self.connected:
            self.make_connection()
        # Insert the vectors into the collection
        return self.client.insert(self.collection_name, records=vectors)

    def search_vectors(self, query_vector, top_k=10):
        if not self.connected:
            self.make_connection()
        #collection_name = "sophia_embeddings"
        #config.logger.debug(f"Searching for similar vectors to query vector: {query_vector}")
        try:
            # Search for similar vectors in the collection
            search_params = {"metric_type": "L2", "params": {"nprobe": 16}}
            results = self.collection.search(data=[query_vector], anns_field="embeddings", param=search_params, limit=10) #, index_param=index_param)
            #results = self.collection.search("sophia", 10, [query_vector])
            config.logger.debug(f"Search results: {results}")
            return results
        except Exception as e:
            print(f"Milvus search exception: {e}")

    def delete_vectors(self, collection_name, ids):
        if not self.connected:
            self.make_connection()
        # Delete vectors by their IDs
        self.client.delete_entity_by_id(collection_name, ids)

    def drop_collection(self, collection_name):
        if not self.connected:
            self.make_connection()
        # Drop the entire collection
        self.client.drop_collection(collection_name)
