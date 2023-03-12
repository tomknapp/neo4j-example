// Create the schema - Define indexes for MERGE statements below
CREATE INDEX ix_noun_phrases FOR (a:Phrase) ON (a.noun_phrase);
CREATE INDEX ix_message_id FOR (a:Message) ON (a.message_uuid);
CREATE INDEX ix_timestamp FOR (a:Message) ON (a.timestamp);
CREATE INDEX ix_identity_id FOR (a:Identity) ON (a.identity_id);
CREATE INDEX ix_candidate_id FOR (a:Candidate) ON (a.candidate_id);


// message_uuid,module,level,message,identity_id,candidate_id,timestamp
LOAD CSV WITH HEADERS FROM "file:///message_nodes.csv" AS row
MERGE (m:Message {message_uuid: row.message_uuid, module: row.module, level: row.level, message: row.message, identity_id: coalesce(row.identity_id, "Unknown"), candidate_id: coalesce(row.candidate_id, "Unknown"), timestamp: datetime(row.timestamp)});

// message_uuid,candidate_id
LOAD CSV WITH HEADERS FROM "file:///candidate_relationships.csv" AS row
MERGE (m:Candidate {candidate_id: row.candidate_id});

LOAD CSV WITH HEADERS FROM "file:///candidate_relationships.csv" AS row
MATCH (m:Message {message_uuid: row.message_uuid})
MATCH (c:Candidate {candidate_id: row.candidate_id})
MERGE (m)-[:ENTRY_ABOUT]->(c);

// message_uuid,identity_id
LOAD CSV WITH HEADERS FROM "file:///identity_relationships.csv" AS row
MERGE (m:Identity {identity_id: row.identity_id});

LOAD CSV WITH HEADERS FROM "file:///identity_relationships.csv" AS row
MATCH (m:Message {message_uuid: row.message_uuid})
MATCH (i:Identity {identity_id: row.identity_id})
MERGE (m)-[:ENTRY_ABOUT]->(i);

// message_uuid,noun_phrase
LOAD CSV WITH HEADERS FROM "file:///phrase_relationships.csv" AS row
MERGE (m:Phrase {noun_phrase: row.noun_phrase});

LOAD CSV WITH HEADERS FROM "file:///phrase_relationships.csv" AS row
MATCH (m:Message {message_uuid: row.message_uuid})
MATCH (p:Phrase {noun_phrase: row.noun_phrase})
MERGE (m)-[:CONTAINS]->(p);
