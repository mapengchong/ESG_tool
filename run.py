import pandas as pd
from rapidfuzz import fuzz
from neo4j import GraphDatabase
from datetime import datetime as dt


""" Relies on gene_data_locus.csv, a file which has two columns, 'stdname' and 'sysname'. 
    Every row has a sysname defined, but some rows display 'UNCHARACTERIZED'. Create a
    dictionary of the uppercased names, using sysname as key when stdname unavailable."""
def create_name_dict():
    name_dict = {}
    name_df = pd.read_csv("archive/gene_data_locus.csv")
    for i in range(len(name_df)):
        std = name_df['stdname'][i].upper()
        sys = name_df['sysname'][i].upper()
        if std != "UNCHARACTERIZED":
            name_dict[std] = sys
        else: 
            name_dict[sys] = sys
    return name_dict

""" Remove the 'p' from all stdnames in 'proteinname' column, uppercase all if not already.
    Add a new column matching the sysname to stdname and return the resulting dataframe """
def standardize_func_df():
    func_df = pd.read_csv("archive/gene_data_GO.csv")
    name_dict = create_name_dict()
    cut = []
    for x in func_df['proteinname']:
      if x[-1] == 'p':
        cut.append(x[0:-1].upper())
      else:
        cut.append(x.upper())
    func_df['proteinname'] = cut
    func_df['sysname'] = [name_dict[std] for std in func_df['proteinname']]
    return func_df

""" To prepare for comparison of every row by rapidfuzz, take all relevant columns of our func_df
    and combine them into one column, which is returned """
def get_combined_df():
    func_df = standardize_func_df()
    func_df['combined_text'] = func_df['description'] + func_df['go_BioProc'] + func_df['go_MolFunc'] + func_df['go_CellComp']
    func_df.drop(['go_BioProc', 'description', 'go_MolFunc', 'go_CellComp'], axis=1, inplace=True)
    return func_df

def write_truncated():
    func_df = standardize_func_df()
    func_df['go_MolFunc'] = [x.split(':')[0] for x in func_df['go_MolFunc']]
    func_df['go_CellComp'] = [x.split(':')[0] for x in func_df['go_CellComp']]
    func_df['go_BioProc'] = [x.split(':')[0] for x in func_df['go_BioProc']]
    func_df.to_csv("archive/truncated.csv")

class Neo4j_Connection:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
        
    """ Use the rapidfuzz library to compare similarity ratios between every row and every 
        other single row. Store the resulting score as a relationship between two genes in 
        the database, if the score is above the specified threshold. """
    def initialize_scores(self, threshold):
        df = get_combined_df()
        names = df['proteinname'].to_list()
        comparisons = df['combined_text'].to_list()
        with self.driver.session() as session:
            # Timer for comparison between runs
            start = dt.now()
            for i in range(len(names)):
                for j in range(i+1, len(names)):
                    score = fuzz.ratio(comparisons[i], comparisons[j])
                    if score > threshold:
                        session.write_transaction(self._create_score_relationship, names[i], names[j], score)
            end = dt.now()
            print(f'Time running with threshold as {threshold} is {end - start}')

    
    @staticmethod
    def _create_score_relationship(tx, node1, node2, score):
        result = tx.run("""
        MATCH (p1:Protein), (p2:Protein)
        WHERE p1.name = $node1 AND p2.name = $node2
        MERGE (p1)-[r1:SIMILARTO {score: $score}]-(p2)
        """, node1=node1, node2=node2, score=score)
        return result
    
    def get_most_similar(self, name, x):
        with self.driver.session() as session:
            result = session.write_transaction(self._return_x_similar, name, x)

    @staticmethod
    def _return_x_similar(tx, name, x):
        top_x = []
        lim=90
        query = "MATCH (p:Protein) -[r:SIMILARTO]-(a:Protein) WITH r, p, a ORDER BY r.score DESC WHERE p.name = $name return p.name, a.name LIMIT $x" 
        print(query)
        result = tx.run(query, name=name, x=x)
        for line in result:
            top_x.append(line.values()[1])
        for element in top_x:
            query = "MATCH (s) WHERE s.name = $name RETURN s"
            result = tx.run(query, name=element)
            for element in result: print(f'{element[0]["name"]}: {element[0]["description"]}')#This is accessing the properties data from our node, then indexing at key description.
        
    """ Populate database with naive method of representing relationships. Make sure
    you have truncated.csv in the import directory of Neo4j for desktop """
    def initialize_naive(self):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_naive)
    

    """ The original established Cypher query for creating our database. Note, you must
    have truncated.csv in the import directory of Neo4j for desktop """
    @staticmethod
    def _create_and_return_naive(tx):
        result = tx.run("""
            LOAD CSV WITH HEADERS FROM "file:///truncated.csv" as line
            MERGE (p:Protein {name: line.proteinname, sysname: line.sysname, description: line.description})
            MERGE (b:BioProc {name: line.go_BioProc})
            MERGE (m:MolFunc {name: line.go_MolFunc})
            MERGE (c:CellComp {name: line.go_CellComp})
            MERGE (p)-[r1:HASBIOPROC]-(b)
            MERGE (p)-[r2:HASMOLFUNC]-(m)
            MERGE (p)-[r3:INCELLCOMP]-(c)
            RETURN (p) 
        """)
        return result


def main():
    # Uncomment write_truncated if you need to generate the file again for some reason
    #write_truncated()

    # Populate the database with the "naive" nodes and then the similarity scores
    conn = Neo4j_Connection("bolt://localhost:7687", "neo4j", "1234")
    #conn.initialize_naive()
    #conn.initialize_scores(threshold=70)
    #conn.get_most_similar("YHR045W", 10)

if __name__ == "__main__":
    main()   
