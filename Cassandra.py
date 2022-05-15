from cassandra.cluster import Cluster

class Cassandra:
    PUBLIC_IP = ""
    session = ""
    keyspace_name = ""
    table_name = ""
    def connect(self, public_ip):
        self.PUBLIC_IP = public_ip
        cluster = Cluster([self.PUBLIC_IP])
        try:
            self.session = cluster.connect()
            name = self.session.execute('select cluster_name from system.local;')
            cluster_name = [i.cluster_name for i in name]
            return f"Connected to {cluster_name[0]} at {self.PUBLIC_IP}"
        except Exception as e:
            message = type(e).__name__
            return message

    def get_keyspaces(self):
        return self.session.execute("desc keyspaces;")

    def get_tables(self, keyspace_name):
        query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{keyspace_name}';"
        return self.session.execute(query)

    def get_data(self, keyspace, table, columns_name):
        query = f"select {', '.join(columns_name)} from {keyspace}.{table}"
        return self.session.execute(query)

    def get_columns_name(self, keyspace, table):
        query = f"select column_name, kind from system_schema.columns where keyspace_name = '{keyspace}' and table_name = '{table}';"
        return self.session.execute(query)

    def createKeyspace(self, query):
        return self.session.execute(query)

    def execute_query(self, query):
        return self.session.execute(query)