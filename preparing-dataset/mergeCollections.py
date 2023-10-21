from smallerDataset import connectMongoDb, getMongoDbCollection


def merge_two_collections():
    db = connectMongoDb()
    collection1 = getMongoDbCollection(collection_name='cracow-attractions-popular', db=db)
    collection2 = getMongoDbCollection(collection_name='cracow-new-attractions', db=db)

    col1_items = collection1.find({})
    col2_items = collection2.find({})

    new_collection = getMongoDbCollection(collection_name='cracow-attractions-v2', db=db)

    new_collection.insert_many(list(col1_items))
    new_collection.insert_many(list(col2_items))


# merge_two_collections()