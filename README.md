# Neo4j Example

This project creates an example neo4j database containing aws cloudwatch log data.

## Nodes
The data is processed to generate nodes of messages, noun phrases and referenced entities.

## Relationships
Relationships are defined to connect:

```cypher
(message)-[:CONTAINS]->(phrase)
```

```cypher
(message)-[:ENTRY_ABOUT]->(entity)
```

## Installation

### Setup the data preparation environment

Create and activate a python virtual enviroment and install the requirements.

Example using [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv):
```zsh
pyenv virtualenv 3.11.1 neo4j-example-3.11.1
pyenv activate neo4j-example-3.11.1
```

Install dependencies via:

```zsh
python3 -m pip install -r requirements/base.txt --no-deps
```

Install the Natural Language Processing (NLP) dataset used by spacy in the **parseMessages.py** script:
```zsh
python -m spacy download en_core_web_sm
```

### Create the neo4j database
* Ensure the project directory contains the required folders:

***
**./persistance** -> (used to map to the docker folders for persisting the neo4j data and logs)

**./data** -> (used to import the csv data into the graph database)
***

* Amend the docker-compose.yaml file to contain your chosen password for the neo4j password (Replacing: \<YOUR SECURE PASSWORD\>).

* Download the required neo4j docker image and create a container using docker compose:

```zsh
docker compose up -d
```

## Prepare the data

1. Download the required AWS Cloudwatch log files in json format and place in a directory accessible to this project.

2. Run the ***parseMessages.py*** script to generate the files required for import.

Usage:

```zsh
❯ python -m parseMessages -h
usage: parseMessages.py [-h] logFile message_nodes phrase_relationships identity_relationships candidate_relationships

positional arguments:
  logFile               (In) AWS log exported in json format
  message_nodes         (Out) CSV file containing message node data
  phrase_relationships  (Out) CSV file containing message -> noun phrase relationships
  identity_relationships
                        (Out) CSV file containing message -> identity entity relationships
  candidate_relationships
                        (Out) CSV file containing message -> candidate entity relationships

options:
  -h, --help            show this help message and exit
```

Example:

```zsh
cd scripts
python -m parseMessages "../data/logs-insights-results.json" "../data/message_nodes.csv" "../data/phrase_relationships.csv" "../data/identity_relationships.csv" "../data/candidate_relationships.csv"
```

## Load the data into neo4j
(Data is imported using the CSV importer and requires the project **./data** folder containing the csv files to be volume mounted to the neo4j docker image **/import** folder).

* Navigate to the neo4j browser: http://localhost:7474/browser/

* Connect using the credentials defined in the ***docker-compose.yaml*** file (NEO4J_AUTH: username/password).

* Run the commands contained in **./scripts/import-commands.cypher** in the neo4j browser.

(Amend any file names/paths to relate to the data files generated when preparing the data).

## Cypher
* Query the data in the database using the cypher query language: https://neo4j.com/docs/cypher-manual/current/

* Cheat Sheet: https://neo4j.com/docs/cypher-cheat-sheet/current/

Example returning messages in a date range:

```cypher
MATCH (m:Message) WHERE m.timestamp > datetime("2023-03-07T15:02:45.607394000Z") AND m.timestamp < datetime("2023-03-07T15:02:45.630150000Z") RETURN m;
```
Or with less granular timestamps:

```cypher
MATCH (m:Message) WHERE m.timestamp > datetime("2023-03-07T15:02:45") AND m.timestamp < datetime("2023-03-07T15:02:46") RETURN m;
```

Finding all entities that have messages mentioning a string:

```cypher
MATCH (i:Identity)--(m:Message)--(p:Phrase WHERE left(p.noun_phrase, 7) = 'success') RETURN i.identity_id, m.message, m.timestamp;
```

(With relationships, incl. direction defined):

```cypher
MATCH (i:Identity)<-[:ENTRY_ABOUT]-(m:Message)-[:CONTAINS]->(p:Phrase WHERE left(p.noun_phrase, 7) = 'success') RETURN i.identity_id, m.message, m.timestamp;
```

## Getting Funky - Graph Algorithms

Neo4j provides a suite of graph algorithms to explore and analyse graph databases: https://neo4j.com/docs/graph-data-science/current/algorithms/

### Page Rank Example
You can run the page rank graph algorithm on the impored data to find the most linked to noun phrases by the imported log message.

* Run the commands contained in **./scripts/page-rank.cypher** in the neo4j browser.


## Making Changes
Whenever any changes are made to the requirements/base.txt file, run the command:

```bash
pip freeze --requirement requirements/base.txt > requirements/base.lock
```
