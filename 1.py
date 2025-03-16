from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"  # 确保 Neo4j 服务地址正确
NEO4J_USER = "neo4j"  # 确保用户名正确
NEO4J_PASSWORD = "xuweiyuan"  # 确保密码正确

# 测试连接函数
def test_neo4j_connection(uri, user, password):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j Connection Successful' AS message")
            for record in result:
                print(record["message"])
        driver.close()
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")

# 调用测试函数
test_neo4j_connection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
