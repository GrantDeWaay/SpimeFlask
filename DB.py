from dotenv import dotenv_values
from neo4j import GraphDatabase

from enums import OPS


# TODO: OBJECT RELATIONAL MAPPING

# TODO: Use google maps API to map routes, make connections, give locations PlaceIDs and estimate
#		time of arrival and emissions to generate ESG reports
class DB(object):
    config = dotenv_values(".env")

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
                return session.execute_write(self._post_location, data)
            elif operation == OPS.DELETE_ALL_TRANSACTIONS:
                if data == self.config["ADMIN-CODE"]:
                    return session.execute_write(self._delete_all_transactions)
                else:
                    return "Incorrect Admin Code, "
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
                        "	(t)<-[:HEAD]-(c)-[:MOVED]->(t), "
                        "	(t)-[:SENT_TO]->(l) "
                        "RETURN c as c", id=data['locid'])
        return [{"crateid": record["c"]["id"]}
                for record in result], 200

    @staticmethod
    def _post_location(tx, data):
        result = tx.run("CREATE (l:Location {id: apoc.create.uuid(), name: $name}) "
                        "RETURN l", name=data["name"])
        return [{"locid": record["l"]["id"]}
                for record in result], 200

    # Removed feature, won't be done in time for demo
    #
    # @staticmethod
    # def _post_approved_connection(tx, data):
    # 	tx.run("MATCH (lFrom:Location) "
    # 		   "WHERE lFrom.id = $loc1id "
    # 		   "MATCH (lTo:Location) "
    # 		   "WHERE lTo.id = $loc2id "
    # 		   "CREATE (lFrom)-[:APPROVED_ROUTE]->(lTo)", loc1id=data["loc1"], loc2id=data["loc2"])
    # 	return "", 200
    #
    # @staticmethod
    # def _get_approved_connections(tx, data):
    # 	result = tx.run("MATCH (l:Location)-[:APPROVED_ROUTE]->(lr:Location) "
    # 					"WHERE l.id = $locid "
    # 					"RETURN lr as lr ", locid=data['locid'])
    # 	return [{"locid": record["lr"]["id"]}
    # 			for record in result], 200

    @staticmethod
    def _get_location(tx, data):
        result = tx.run("MATCH (l:Location) "
                        "WHERE l.id = $id "
                        "RETURN l as Locations", id=data['locid'])
        return [record["Locations"] for record in result].__str__(), 200

    @staticmethod
    def _get_locations(tx, data):
        result = tx.run("MATCH (l:Location) "
                        "RETURN l as Locations", id=data['locid'])
        return [(record["Locations"], record['']) for record in result].__str__(), 200

    @staticmethod
    def _get_crate(tx, data):
        result = tx.run("MATCH (c:Crate) "
                        "WHERE c.id = $id "
                        "RETURN c as Crates", id=data['crateid'])
        return [record["Crates"] for record in result].__str__(), 200

    # Hey how about we don't have an endpoint that deletes everything
    #
    # @staticmethod
    # def _delete_all(tx):
    # 	tx.run("MATCH (n) "
    # 		   "DETACH DELETE n")
    # 	return "", 200

    @staticmethod
    def _delete_all_transactions(tx):
        tx.run("MATCH (n:Transaction) "
               "DETACH DELETE n")
        return "", 200

    @staticmethod
    def _post_transaction(tx, data):
        result = tx.run("MATCH "
                        "(c:Crate {id: $id})-[r:HEAD]->(tOld:Transaction), "
                        "(l:Location {id: $sentto}) "
                        "DELETE r "
                        "CREATE (tNew:Transaction {timestamp: localdatetime.transaction()}), "
                        "(c)-[:HEAD]->(tNew)-[:SENT_TO]->(l), "
                        "(tOld)-[:MOVED]->(tNew) "
                        "RETURN tNew as Transaction", id=data["crateid"], sentto=data["locid"])
        return [{"Transaction": record["Transaction"]["timestamp"].strftime("%m/%d/%Y, %H:%M")}
                for record in result], 200

    @staticmethod
    def _del_transaction_pop(tx, data):
        result = tx.run("MATCH "
                        "(c:Crate {id: $id})-[r:HEAD]->(tOld:Transaction),")
    @staticmethod
    def _get_all_transactions_of_crate(tx, data):
        result = tx.run("MATCH (c:Crate {id: $id})-[:MOVED*]->(tList:Transaction)-[:SENT_TO]->(lList:Location) "
                        "RETURN tList AS Transactions, lList AS Locations", id=data)
        return [(record["Transactions"]["timestamp"].strftime("%m/%d/%Y, %H:%M"), record["Locations"]["name"]) for
                record in result]
# Do not use loops if you care about performace in python, try to refactor it into a vector operator or something
