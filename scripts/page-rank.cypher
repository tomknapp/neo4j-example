// Graph Data Science - Page Rank Example
// ======================================
// https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/

// Project a named graph using a native projection and store it in the graph catalog
CALL gds.graph.project(
  'myGraph',
  ['Message', 'Phrase'],
  'CONTAINS'
)

// Estimate the memory requirements for running the algorithm
CALL gds.pageRank.write.estimate('myGraph', {
  writeProperty: 'pageRank',
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory

// Run the algorithm in stream mode
CALL gds.pageRank.stream('myGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).noun_phrase AS phrase, score
ORDER BY score DESC, phrase ASC