from pymongo import MongoClient

# 连接 MongoDB
# 选择数据库（不存在则自动创建）
# 选择集合（不存在则自动创建）
client = MongoClient("mongodb://admin:123456@49.232.158.128:27017/?authSource=admin")
db = client["mydb"]
collection = db["students"]


def test_create_collection():
    print("连接成功！")
    return collection

def test_insert(collection):
    result = collection.insert_one({
    "name": "张三",
    "age": 20,
    "major": "计算机科学"
    })
    print(f"插入成功，ID: {result.inserted_id}")

    results = collection.insert_many([
        {"name": "李四", "age": 22, "major": "软件工程"},
        {"name": "王五", "age": 21, "major": "计算机科学"},
    ])
    print(f"插入 {len(results.inserted_ids)} 条记录")
def test_select(collection):
    for doc in collection.find():
        print(doc)
    for doc in collection.find({"major": "计算机科学"}):
        print(doc["name"],doc["age"])
    student = collection.find_one({"name": "张三"})
    print(student)
    print("============================")
    for doc in collection.find().sort([("age", -1)]).limit(2):
        print(doc["name"],doc["age"])

def test_update(collection):
    # 更新单条
    result = collection.update_one(
        {"name": "张三"},  # 查询条件
        {"$set": {"age": 21}}  # 更新操作
    )
    print(f"匹配 {result.matched_count} 条，修改 {result.modified_count} 条")

    # 更新多条
    result = collection.update_many(
        {"major": "计算机科学"},
        {"$set": {"status": "在读"}}
    )
    print(f"修改 {result.modified_count} 条")

def test_delete(collection):
    # 删除单条
    result = collection.delete_one({"name": "王五"})
    print(f"删除 {result.deleted_count} 条")

    # 删除多条
    result = collection.delete_many({"age": {"$lt": 21}})
    print(f"删除 {result.deleted_count} 条")

if __name__ == '__main__':
    collection = db["students"]
    # test_create_collection()
    # test_insert(collection)
    # test_select(collection)
    # test_update(collection)
    test_delete(collection)