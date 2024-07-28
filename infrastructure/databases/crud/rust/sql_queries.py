GET_ALL_NODES = """
SELECT * FROM test_schema.nodes;
"""

GET_ALL_NODES_LIMITED = """
SELECT * FROM test_schema.nodes LIMIT :limit;
"""
