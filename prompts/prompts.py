# prompts.py
DEFAULT_PROMPT = """                        
                        Instruction to Agent:
                        Your name is Sophia and you are a highly intelligent assistant capable of understanding the intent of your user. 
                        When receiving new input, you will analyze it to determine if clarification is required, such as
                        the query contains too much ambiguity, is missing information, or is simply too broad a question.
                       
                        If you are unable to answer the query, you will say so.
                        
                        use LaTeX to write mathematical equations in Markdown
                        
                        For example:
                            For a single-line equation, use a single dollar sign before and after the equation, like this: $E=mc^2$.
                            For a multi-line equation, use two dollar signs before and after the equation, like this: $$E=mc^2$$
                       
"""

SUMMARY_PROMPT = """
        Please summarize the preceding conversation. Please don't neglect to include the factual content when 
        summarizing. Please omit any mention of the user's confirmation at the end. It's sufficient to summarize the 
        conversation up to the point of the user's confirmation.
"""

KG_QUERY_PROMPT = """
Generate a Cypher query to retrieve entities and their relationships from the knowledge graph related to the topic of interest. The query should identify nodes and edges that are directly and indirectly associated with this topic, providing a comprehensive overview of the existing data landscape. This will inform the integration of new information related to the topic, ensuring relevance and preventing duplication. Consider including entities of various types and their connections that could be pertinent.

You must account for routine differences in the text, such as capitalization and pluralization, to ensure the query is robust and can handle variations in the input data.
Example:
    Topic of interest: derivatives
    Output: 
        MATCH (n)-[r]-(m)
        WHERE toLower(n.name) CONTAINS 'derivatives'
        RETURN n, r, m
Your reply must be a valid Cypher query that can be executed in a Neo4j instance. Include no extraneous text. Failure to provide a valid query will result in a negative reward.
Topic of Interest: {topic}
"""

KG_PROMPT = """
Translate the following descriptive text into a valid Cypher query that models the information using Neo4j. The description is based on schema.org standards, so please identify relevant schema.org types and properties to structure the data accurately within the Neo4j database. Ensure to use MERGE to avoid creating duplicate nodes, SET for adding or updating properties, and properly define relationships between entities. Here's the description provided:

    Guidelines:

    Identify Entities: Determine the main entities described in the text and their corresponding schema.org types.
    Extract Properties: Extract key details about these entities to use as properties in the database, aligning with schema.org properties where possible.
    Define Relationships: Identify any relationships between entities mentioned in the text and represent these relationships in your query.
    Use MERGE and SET Appropriately: Utilize MERGE to handle entities and relationships to ensure no duplicates are created. Use SET to add or update properties on entities and relationships based on the information provided.
    Return Statement: Include a RETURN statement at the end of your query to display the created or updated entities.
    Do not include any extraneous text as this query will be used directly in a Neo4J instance.

    Examples:

    Example 1 Input: Describe the formation of the solar system.
    Example 1 Output: MERGE (solarSystemFormation:Event {{name: 'Formation of the Solar System'}})
        SET solarSystemFormation.description = 'Began with the gravitational collapse of a small part of a giant molecular cloud. Most of the collapsing mass collected in the center, forming the Sun, while the rest flattened into a protoplanetary disk out of which the planets, moons, and other objects formed.'
        MERGE (molecularCloud:Material {{name: 'Giant Molecular Cloud'}})
        MERGE (sun:CelestialBody {{name: 'Sun'}})
        MERGE (protoplanetaryDisk:Material {{name: 'Protoplanetary Disk'}})
        MERGE (molecularCloud)-[:COLLAPSED_TO_FORM]->(solarSystemFormation)
        MERGE (solarSystemFormation)-[:LED_TO_CREATION_OF]->(sun)
        MERGE (solarSystemFormation)-[:LED_TO_CREATION_OF]->(protoplanetaryDisk)
        RETURN solarSystemFormation, molecularCloud, sun, protoplanetaryDisk;

    Example 2 Input: Describe the process of water turning into ice within the context of a physical change. Include the states of water and ice, and the process of freezing 
    Example 2 Output:
        MERGE (water:State {{name: 'Water', temperature: 'Above 0°C'}})
        SET water.description = 'Liquid state of H2O, typically found at temperatures above 0°C.'
        MERGE (ice:State {{name: 'Ice', temperature: '0°C and below'}})
        SET ice.description = 'Solid state of H2O, formed when water freezes at 0°C.'
        MERGE (freezing:Process {{name: 'Freezing'}})
        SET freezing.description = 'The physical process where liquid water turns into ice when the temperature drops to 0°C or below.'
        MERGE (water)-[:UNDERGOES]->(freezing)-[:RESULTS_IN]->(ice)
        RETURN water, freezing, ice;

EXISTING DATA: 
    {existing_data}
IT IS ESSENTIAL THAT ALL SPECIAL CHARACTERS ARE ESCAPED IN THE RETURNED QUERY.
IT IS ESSENTIAL THAT THE RETURNED QUERY IS IN A VALID CYPHER FORMAT THAT CAN BE EXECUTED WITHOUT ERROR IN NEO4J.
FAILURE WILL RESULT IN A NEGATIVE REWARD.

    Input Text: {user_input}
    Output Cypher Query:
"""

KG_PROMPT2 = """
Translate the following descriptive text into a valid Cypher query that models the information using Neo4j. The description is based on schema.org standards, so please identify relevant schema.org types and properties to structure the data accurately within the Neo4j database. Ensure to use MERGE to avoid creating duplicate nodes, SET for adding or updating properties, and properly define relationships between entities. Here's the description provided:

    Guidelines:

    Identify Entities: Determine the main entities described in the text and their corresponding schema.org types.
    Extract Properties: Extract key details about these entities to use as properties in the database, aligning with schema.org properties where possible.
    Define Relationships: Identify any relationships between entities mentioned in the text and represent these relationships in your query.
    Use MERGE and SET Appropriately: Utilize MERGE to handle entities and relationships to ensure no duplicates are created. Use SET to add or update properties on entities and relationships based on the information provided.
    Return Statement: Include a RETURN statement at the end of your query to display the created or updated entities.
    Do not include any extraneous text as this query will be used directly in a Neo4J instance.

    Examples:

    Example 1 Input: Describe the formation of the solar system.
    Example 1 Output: MERGE (solarSystemFormation:Event {{name: 'Formation of the Solar System'}})
        SET solarSystemFormation.description = 'Began with the gravitational collapse of a small part of a giant molecular cloud. Most of the collapsing mass collected in the center, forming the Sun, while the rest flattened into a protoplanetary disk out of which the planets, moons, and other objects formed.'
        MERGE (molecularCloud:Material {{name: 'Giant Molecular Cloud'}})
        MERGE (sun:CelestialBody {{name: 'Sun'}})
        MERGE (protoplanetaryDisk:Material {{name: 'Protoplanetary Disk'}})
        MERGE (molecularCloud)-[:COLLAPSED_TO_FORM]->(solarSystemFormation)
        MERGE (solarSystemFormation)-[:LED_TO_CREATION_OF]->(sun)
        MERGE (solarSystemFormation)-[:LED_TO_CREATION_OF]->(protoplanetaryDisk)
        RETURN solarSystemFormation, molecularCloud, sun, protoplanetaryDisk;

    Example 2 Input: Describe the process of water turning into ice within the context of a physical change. Include the states of water and ice, and the process of freezing 
    Example 2 Output:
        MERGE (water:State {{name: 'Water', temperature: 'Above 0°C'}})
        SET water.description = 'Liquid state of H2O, typically found at temperatures above 0°C.'
        MERGE (ice:State {{name: 'Ice', temperature: '0°C and below'}})
        SET ice.description = 'Solid state of H2O, formed when water freezes at 0°C.'
        MERGE (freezing:Process {{name: 'Freezing'}})
        SET freezing.description = 'The physical process where liquid water turns into ice when the temperature drops to 0°C or below.'
        MERGE (water)-[:UNDERGOES]->(freezing)-[:RESULTS_IN]->(ice)
        RETURN water, freezing, ice;

EXISTING DATA: 
    {existing_data}
IT IS ESSENTIAL THAT ALL SPECIAL CHARACTERS ARE ESCAPED IN THE RETURNED QUERY.
IT IS ESSENTIAL THAT THE RETURNED QUERY IS IN A VALID CYPHER FORMAT THAT CAN BE EXECUTED WITHOUT ERROR IN NEO4J.
FAILURE WILL RESULT IN A NEGATIVE REWARD.

    Input Text: {user_input}
    Output Cypher Query:
"""
