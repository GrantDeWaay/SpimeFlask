from dotenv import dotenv_values
from neo4j import GraphDatabase

from StrandRSA import create_keypair
from enums import OPS


class DB(object):
	config = dotenv_values("config.env")
	driver = GraphDatabase.driver(config["URL"], auth=(config["USER"], config["PASSWORD"]))

	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(DB, cls).__new__(cls)
		return cls.instance

	def close(self):
		self.driver.close()

	def execute(self, operation, data=None):
		with self.driver.session() as session:
			if operation == OPS.GET_CRATE:
				return session.execute_write(self._get_crate, data)
			elif operation == OPS.POST_CRATE:
				return session.execute_write(self._post_crate, data)
			elif operation == OPS.GET_LOCATION:
				return session.execute_write(self._get_location, data)
			elif operation == OPS.POST_LOCATION:
				return session.execute_write(self._post_location)
			elif operation == OPS.DELETE_ALL:
				return session.execute_write(self._delete_all)
			elif operation == OPS.POST_TRANSACTION:
				return session.execute_write(self._post_transaction, data)
			elif operation == OPS.GET_TRANSACTIONS:
				return session.execute_write(self._get_all_transactions_of_crate, data)
			else:
				return "Invalid Operation, Server Error", 500

	@staticmethod
	def _post_crate(tx, data):
		result = tx.run("MATCH (l:Location {id: $id}) "
						"CREATE"
						"	(t:Transaction {timestamp: localdatetime.transaction()}), "
						"	(c:Crate {id: apoc.create.uuid()}),"
						"	(t)<-[:HEAD]-(c), "
						"	(c)-[:MOVED]->(t), "
						"	(t)-[:SENT_TO]->(l)"
						"RETURN c as c", id=data)
		return [{"crateid": record["c"]["id"]}
				for record in result], 200

	@staticmethod
	def _post_location(tx):
		result = tx.run("CREATE (l:Location {id: apoc.create.uuid()}) "
						"RETURN l")
		return [{"locid": record["l"]["id"]}
				for record in result], 200

	@staticmethod
	def _get_location(tx, data):
		result = tx.run("MATCH (l:Location) "
						"WHERE l.id = $id "
						"RETURN l as Locations", id=data)
		return [record["Locations"] for record in result].__str__(), 200

	@staticmethod
	def _get_crate(tx, data):
		result = tx.run("MATCH (c:Crate) "
						"WHERE c.id = $id "
						"RETURN c as Crates", id=data)
		return [record["Crates"] for record in result].__str__(), 200

	@staticmethod
	def _delete_all(tx):
		tx.run("MATCH (n) "
			   "DETACH DELETE n")
		return "", 200

	@staticmethod
	def _post_transaction(tx, data):
		result = tx.run("MATCH (tOld:Transaction)<-[r:HEAD]-(c:Crate {id: $id}) "
						"MATCH (l:Location {id: $sentto}) "
						"DELETE r "
						"CREATE (tNew:Transaction {timestamp: localdatetime.transaction()}), "
						"((tNew)<-[:HEAD]-(c)), "
						"((tNew)-[:SENT_TO]->(l)), "
						"((tOld)-[:MOVED]->(tNew))", id=data[0], sentto=data[1])
		return "i mean it works ig", 200

	@staticmethod
	def _get_all_transactions_of_crate(tx, data):
		result = tx.run("MATCH (tStart:Transaction)<-[:MOVED]-(c:Crate {id: $id}) "
						"MATCH p = (tStart)-[:MOVED*]->(x:Transaction) "
						"RETURN x AS Transactions", id=data)
		return [record["Transactions"] for record in result]
# Do not use loops if you care about performace in python, try to refactor it into a vector operator or something
