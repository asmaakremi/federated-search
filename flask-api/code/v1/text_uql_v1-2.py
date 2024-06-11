from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests
from datetime import datetime, timezone
import re

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "https://vdevpril922dsy.dsone.3ds.com:444","https://ve4al631sy.dsone.3ds.com:444","https://dsext001-eu1-215dsi0708-ifwe.3dexperience.3ds.com"]) 

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def call_llm(prompt) :
    url = 'http://px101.prod.exalead.com:8110/v1/chat/completions'
    headers = {
        'Authorization': 'Bearer vtYvpB9U+iUQwl0K0MZIj+Uo5u6kilAZJdgHGVBEhNc=',
        'Content-Type': 'application/json'
    }
    messages = [{"role": "user", "content": prompt}]
    payload = {
        "model":"meta-llama/Meta-Llama-3-8B-Instruct",
        "messages": messages,  
        "max_tokens": 500,
        "top_p": 1,
        "stop": ["string"],
        "response_format": {
            "type": "text", 
            "temperature": 0.7
        }
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        generated_response = response.json()['choices'][0]['message']['content'].strip()
        return generated_response
    else:
        return f"Failed to generate response. Status code: {response.status_code}\nResponse: {response.text}"

    
def text_to_uql(query):
    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    prompt = f"""
You are an expert in transforming natural language queries into UQL queries using a specified ontology. Based on user questions about data stored in an RDF graph, employ the provided ontology, documentation, and steps to understand the UQL syntax. Then, generate the UQL query equivalent for the given natural language query. The response should contain only the UQL query without any explanations or additional text.

**Current Date**: {current_date} (Use this date to handle queries involving specific time frames such as 'this year', 'today', etc., by calculating the relevant date ranges.)

** RDF Data Model and Ontology **
    @prefix vpmReference: <http://www.3ds.com/RDF/ontology/archetype/vpmReference#> .
    @prefix physicalProduct: <http://www.3ds.com/RDF/ontology/universe/physicalProduct#> .
    @prefix product: <http://www.3ds.com/RDF/ontology/universe/product#> .
    @prefix archetype: <http://www.3ds.com/RDF/ontology/archetype#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
    @prefix owl: <http://www.w3.org/2002/07/owl#> 
    @prefix prov: <http://www.w3.org/ns/prov#> 
    @prefix ds6w: <http://www.w3.org/ds6w#> 
    @prefix dsqt: <http://www.3ds.com/RDF/Corpus/dsqt/> 
    @prefix pno: <http://www.3ds.com/RDF/ontology/archetype/person#> 
    @prefix swym: <http://www.3ds.com/RDF/ontology/archetype/swym#>
    vpmReference: a owl:Ontology ;
        rdfs:comment "Physical Product archetype  .Represents physical products within the system and is equivalent to any general product classification. "@en .
    pno: a owl:Ontology ;
        rdfs:comment "An ontology defining properties of persons."@en .
    swym: a owl:Ontology ;
        rdfs:label "SWYM Social Media Ontology"@en ;
        rdfs:comment "An ontology for describing social media structures including posts, comments, and user interactions."@en ;
    vpmReference:VPMReference rdf:type owl:Class ;
        rdfs:subClassOf archetype:Archetype ;
        rdfs:comment "Physical Product and is equivalent to any general product classification archetype"@en .
    pno:Person rdf:type owl:Class ;
        rdfs:label "Person"@en ;
        rdfs:comment "Represents an individual person."@en .
    physicalProduct:PhysicalProduct rdf:type owl:Class ;
        owl:equivalentClass vpmReference:VPMReference .
    product:Product rdf:type owl:Class ;
        owl:equivalentClass vpmReference:VPMReference .
    Document rdf:type owl:Class ;
        rdfs:comment "General class for documents."@en .
    SocialContent rdf:type owl:Class ;
        rdfs:comment "Content generated in social platforms, like posts, comments, or likes."@en .
    PLMDMT_DocCustom rdf:type owl:Class ;
        rdfs:subClassOf Document ;
        rdfs:comment "A customized document type within the PLM system."@en .
    PLMDMTDocument rdf:type owl:Class ;
        rdfs:subClassOf Document ;
        rdfs:comment "A standard document type for engineering documents within the PLM system."@en .
    AecMember rdf:type owl:Class ;
        rdfs:subClassOf pno:Person ;
        rdfs:comment "A member of an AEC (architecture, engineering, and construction) project."@en .
    3DShape rdf:type owl:Class ;
        rdfs:comment "Represents a 3D shape model in the system."@en .
    swym:Post rdf:type owl:Class ;
        rdfs:subClassOf SocialContent ;
        rdfs:comment "A post within the social collaboration platform."@en .
    ds6w:type rdf:type owl:DatatypeProperty;
        rdfs:label "Type"@en;
        rdfs:comment "Specifies the type of object."@en;
        rdfs:domain [ rdf:unionOf (PLMDMT_DocCustom PLMDMTDocument AecMember pno:Person vpmReference:VPMReference Document 3DShape swym:Post) ];
        rdfs:range xsd:string.
    ds6w:modified rdf:type owl:DatatypeProperty;
        rdfs:label "Modified"@en;
        rdfs:comment "Date and time of last modification."@en;
        rdfs:domain [ rdf:unionOf (PLMDMT_DocCustom PLMDMTDocument AecMember vpmReference:VPMReference Document 3DShape swym:Post) ];
        rdfs:range xsd:dateTime.
    ds6w:created rdf:type owl:DatatypeProperty;
        rdfs:label "Created"@en;
        rdfs:comment "Date and time of creation."@en;
        rdfs:domain [ rdf:unionOf (PLMDMT_DocCustom PLMDMTDocument AecMember vpmReference:VPMReference Document 3DShape swym:Post) ];
        rdfs:range xsd:dateTime.
    ds6w:lastModifiedBy rdf:type owl:ObjectProperty;
        rdfs:label "Last Modified By"@en;
        rdfs:comment "The person who did the last modification."@en;
        rdfs:domain [ rdf:unionOf (PLMDMT_DocCustom PLMDMTDocument AecMember vpmReference:VPMReference Document 3DShape swym:Post) ];
        rdfs:range pno:Person.
    ds6w:responsible rdf:type owl:ObjectProperty;
        rdfs:label "Responsible"@en;
        rdfs:comment "The person responsible for the entity."@en;
        rdfs:domain [ rdf:unionOf (PLMDMT_DocCustom PLMDMTDocument AecMember vpmReference:VPMReference Document 3DShape swym:Post) ];
        rdfs:range pno:Person.
    ds6w:Comments rdf:type owl:DatatypeProperty;
        rdfs:label "Comments"@en;
        rdfs:comment "Number of comments for the post."@en;
        rdfs:domain swym:Post;
        rdfs:range xsd:integer.
    ds6w:endorsements rdf:type owl:DatatypeProperty;
        rdfs:label "Likes"@en;
        rdfs:comment "Number of Likes for the post."@en;
        rdfs:domain swym:Post;
        rdfs:range xsd:integer.
    ds6w:contentStructure rdf:type owl:DatatypeProperty;
        rdfs:label "Content Structure"@en;
        rdfs:comment "Content structure of the product, indicating its hierarchy within the overall design or assembly . This property is applicable exclusively to instances of the vpmReference:VPMReference class"@en;
        rdfs:domain [ rdf:unionOf (vpmReference:VPMReference, 3DShape) ];
        rdfs:range xsd:string;
        owl:oneOf ("Root" "Leaf" "Intermediate" "Standalone").
    ds6w:docExtension rdf:type owl:DatatypeProperty;
        rdfs:label "Document Extension"@en;
        rdfs:comment "The file format of the document, restricted to specific extensions."@en;
        rdfs:domain [ rdf:unionOf (PLMDMT_DocCustom, PLMDMTDocument, AecMember, vpmReference:VPMReference, Document, 3DShape, swym:Post) ];
        rdfs:range xsd:string;
        owl:oneOf ("jpg" "idx" "docx" "pdf" "stp" "xls" "doc" "txt").
    ds6w:businessRole rdf:type owl:DatatypeProperty ;
        rdfs:label "Role"@en ;
        rdfs:comment "The role or job title of the person."@en ;
        rdfs:domain pno:person ;
        rdfs:range xsd:string .
        owl:oneOf ("Strategy & Managemenent" "engineer" "software engineer" "Data Scientist").
    pno:name rdf:type owl:DatatypeProperty ;
        rdfs:label "Name"@en ;
        rdfs:comment "The full name of the person."@en ;
        rdfs:domain pno:Person ;
        rdfs:range xsd:string .

    # Example triple : 
    :doc001 rdf:type Document ;
        ds6w:type "PLMDMTDocument" ;
        ds6w:docExtension "pdf" ;
        ds6w:created "2024-06-01T00:00:00Z"^^xsd:dateTime ;
        ds6w:modified "2024-06-05T00:00:00Z"^^xsd:dateTime ;
        ds6w:responsible person123 ;
        ds6w:lastModifiedBy person124 ;

    :product01 rdf:type VpmReference ;
        ds6w:type "VpmReference" ;
        ds6w:created "2024-06-01T00:00:00Z"^^xsd:dateTime ;
        ds6w:modified "2024-06-05T00:00:00Z"^^xsd:dateTime ;
        ds6w:responsible person123 ;
        ds6w:lastModifiedBy person124 ;
        ds6w:contentStructure "Root".

    pno:person123 rdf:type pno:Person ;
        pno:name "person123" ;
        ds6w:businessRole "VP" ;

    pno:person124 rdf:type pno:Person ;
        pno:name "person124" ;
        ds6w:businessRole "Data Scientist" ;

    swym:post001 rdf:type swym:Post ;
        ds6w:Comments 5 ;
        ds6w:endorsements 10.
        ds6w:lastModifiedBy person124 ;

** UQL Documentation **
    UQL queries are expressed in a pseudo UQL format with operators like AND, OR, NOT. Attribute names should be placed in square brackets. Special characters in attribute names need to be escaped with '\\\\'. 
    1. **Basic UQL Structure**:
        - Attribute names cannot contain characters like .:%#[]$;{{}}.
        - A mapping service translates the names exposed to the user and the names used by Cloudview.
        - Use square brackets for predicate names. If a predicate is unknown, replace it with #false.
        - Escape the first square bracket ‘[’ with ‘\\\\’ to cancel the attribute name mapping, or use quotes ‘“’ to disable it inside quotes.
    3. **Special Cases and Options**:
        - enable_mono_sixw: Enable ds6w split for the query.
        - with_synthesis_ranged: Include ranged facets in the synthesis.
        - facet_params: Customize depth and width of synthesis for given predicates.
    5. **Order Field**:
        - Defines the sort criterion. Less than 1000 objects: sort on any predicates. More than 1000 objects: sort on specific attributes like relevance, ds6w:modified, ds6w:created, ds6w:responsible, ds6w:label.

**Detailed UQL Query Construction Process **
    1. **Identify Relevant Classes and Properties**: Review the ontology to determine which classes or properties are relevant to the query.
    2. **Map Natural Language to RDF Classes**: Use the ontology to correlate the identified natural language elements with the appropriate RDF classes and predicates.Translate terms like 'physical products' and 'products' directly to their RDF class equivalents based on their definitions or equivalences in the ontology.
     - Specifically, treat 'physical products' and 'products' as synonymous with the 'VPMReference' classification in the RDF ontology.
    3. **Construct the UQL Query**: Formulate the UQL query based on these mappings, ensuring to use only those RDF classes and properties directly relevant or defined as equivalent.

**Example UQL Query Construction**
    Given the natural language query: "Show me all documents created 1 juin 2024 , by John Doe"
    - **Step 1: Parse the Natural Language Query**
        - Subject: Documents .
        - Predicate: Created by and date of creation .
        - Object: John Doe and 1 juin 2024 .

    - **Step 2: Map to RDF Concepts**
        - "Documents" corresponds to instances of the 'Document' class.
        - "Created by" maps to the 'ds6w:lastModifiedBy' or 'ds6w:responsible'.
        - "Created 1 juin 2024 " maps to 'ds6w:created' .
        - "John Doe" corresponds to instances of the 'Person' class

    - **Step 3: Formulate the UQL Query**
        -[ds6w:created]>=\"2024-06-01T00:00:00.000Z\" AND [ds6w:created]<=\"2024-06-01T23:59:59.000Z\" AND [ds6w:type]:\"Document\" AND (([ds6w:lastModifiedBy]:\"John Doe\" OR [ds6w:responsible]:\"John Doe\")
    
    ** Example UQL Queries **
   - Example 1:
        - Natural Language: give me products that are created between 2024-05-01 to 2024-05-28 by : MCM OCDxComplianceUser
        - UQL: [ds6w:created]>="2024-05-01T00:00:00.000Z" AND [ds6w:created]<="2024-05-28T23:59:59.000Z" AND [ds6w:type]:"VPMReference"  AND (([ds6w:lastModifiedBy]:"MCM OCDxComplianceUser" OR [ds6w:responsible]:"MCM OCDxComplianceUser") 

   - Example 2:
        - Natural Language: search for posts created by enopotionuser01 having number of likes or comments or likes > 0
        - UQL: [ds6w:type]:"swym:Post" And [ds6w:responsible]:"enopotionuser01" AND [ds6w:comments]:>0 AND [ds6w:endorsements]:>0

    - Example 3:
        - Natural Language: give me all documents created by Insp_R1132100512396 EUW12
        - UQL: [ds6w:type]:"Document "AND ((([ds6w:lastModifiedBy]:\"Insp_R1132100512396 EUW12\" OR [ds6w:responsible]:\"Insp_R1132100512396 EUW12\")))"
    
    - Example 4:
        - Natural Language: "Find me all physical products."
        - UQL: [ds6w:type]:"VPMReference"

    - Example 5:
        - Natural Language: "Find me all products."
        - UQL: [ds6w:type]:"VPMReference"
        This query assumes that 'physical products'and 'products' are defined in the RDF ontology as equivalent to VPMReference, thus not requiring a separate type for 'Product' unless explicitly defined or necessary according to additional ontology information.

Based on the natural language query "{query}" and the current date if needed, generate the corresponding UQL query using the ontology and RDF relationships. Ensure the output strictly adheres to the syntax and ontology requirements without adding or assuming types not explicitly defined.

Please respond ONLY with the valid UQL query.
"""

    try:
        return call_llm(prompt), prompt
    except Exception as e:
        return str(e) 

# def get_reflection_for_uql(full_prompt ,llm_response):
#     reflection_prompt = f"""
#     You were given the following prompt:

#     {full_prompt}

#     Your UQL conversion was:

#     {llm_response}

#     Please review your UQL query and revise it with these guidelines:
#     1. Ensure the response contains only the UQL query—remove any additional text or explanations.
#     2. Confirm all fields are correctly prefixed with 'ds6w:' as specified in the ontology.
#     3. Use logical operators (AND, OR, NOT) correctly within the query.
#     4. Important : Adhere to the required date and number formats as per UQL standards.
#     5. Ensure that all conditions and joins are appropriately represented.
#     6. You are tasked with generating queries based on a specified RDF ontology. When creating queries, it is crucial to respect the domain constraints of properties and the defined relationships between classes. Ensure that each property is used with the correct RDF class according to the ontology's specifications. Verify that the joins in your queries properly reflect the legitimate associations between entities as defined in the ontology.
#     7. [ds6w:contentStructure]  property should not be applied to any other class outside of vpmReference:VPMReference. Using this property with any non-compliant class, such as swym:Post, is incorrect and may lead to data inconsistencies or errors in data interpretation
#     8. Important :handling relative date references such as "this month" , "this year", "today" and "this quarter" Use your understanding of the CURRENT DATE  to dynamically calculate and apply the exact date ranges when processing queries.
#     Please revise your UQL query based on these insights and ensure it strictly adheres to the rules provided.The output should include only the UQL query, strictly adhering to the syntax and ontology requirements without adding or assuming types not explicitly defined as relevant to the query. Respond ONLY with the valid UQL query.
#     """
#     corrected_uql = call_llm(reflection_prompt)
#     return corrected_uql
def get_reflection_for_uql(full_prompt, llm_response, errors):
    reflection_prompt = f"""
    You were given the following prompt:

    {full_prompt}

    Your UQL conversion was:

    {llm_response}

    Here are the list of the errors in your conversion. Please review your UQL query and correct it:

    {' '.join(errors)}
    """
    corrected_uql = call_llm(reflection_prompt)
    return corrected_uql

def validate_uql_response(uql_response):
    corrected = uql_response
    error_messages = []
    rdf_properties = [
        'ds6w:created', 'ds6w:modified', 'ds6w:type', 'ds6w:lastModifiedBy', 
        'ds6w:responsible', 'ds6w:contentStructure'
    ]
    allowed_type_values = [
        'PLMDMT_DocCustom', 'PLMDMTDocument', 'AecMember', 'pno:Person', 
        'VPMReference', 'Document', '3DShape', 'swym:Post'
    ]

    # Validate empty or invalid value comparisons
    invalid_value_pattern = r'\[\w+:\w+\](<>"\\"")'
    invalid_values = re.findall(invalid_value_pattern, uql_response)
    if invalid_values:
        error_messages.append("Error: Invalid or empty value comparisons found.")
        logging.error("Invalid or empty value comparisons found: %s", invalid_values)

    # Check attributes surrounded by incorrect parentheses
    for prop in rdf_properties:
        pattern = rf'\({prop}\)'
        if re.search(pattern, corrected):
            corrected = re.sub(pattern, f'[{prop}]', corrected)
            error_messages.append(f"Error: {prop} should be surrounded by square brackets []. Correction applied.")
            logging.info("%s was surrounded by incorrect brackets, correction applied.", prop)

    # Validate [ds6w:type] values
    type_errors = []
    type_matches = re.findall(r'\[ds6w:type\]:"([^"]+)"', corrected)
    for type_value in type_matches:
        if type_value not in allowed_type_values:
            type_errors.append(type_value)
    if type_errors:
        error_message = ("Error: Invalid type values for [ds6w:type]. The value must be in the list of "
                     f"{allowed_type_values}. Please choose the appropriate type based on the intent of the NLQ "
                     "and avoid adding unauthorized types.")
        error_messages.append(error_message)
        logging.warning("Invalid type values detected: %s", type_errors)

    # Correct unnecessary spaces around colons
    spaces_around_colons = re.findall(r'\[\w+\]\s*:\s*\"[^\"]+\"', corrected)
    for item in spaces_around_colons:
        corrected_item = re.sub(r'\s*:\s*', ':', item)
        corrected = corrected.replace(item, corrected_item)
    if spaces_around_colons:
        error_messages.append("Error: Unnecessary spaces found around colons.")
        logging.info("Unnecessary spaces around colons corrected.")

    # Check datetime format
    datetime_format_errors = []
    for attr in ['created', 'modified']:
        datetime_matches = re.findall(rf'\[ds6w:{attr}\]:"([^"]+)"', corrected)
        datetime_format_errors.extend(
            [match for match in datetime_matches if not re.match(r'\d{4}-\d{2}-\d{2}T00:00:00\.000Z', match)]
        )
    if datetime_format_errors:
        error_messages.append("Error: Invalid datetime format.")
        logging.error("Invalid datetime formats found: %s", datetime_format_errors)

    # Detect incorrect operator usage
    error_pattern = r'\[ds6w:[^\]]+\](?![>=<: ])([^"]+)"'
    errors = re.findall(error_pattern, corrected)
    if errors:
        error_messages.append("Error: Incorrect operator usage detected.")
        logging.error("Incorrect operator usage detected: %s", errors)

    return error_messages, corrected, bool(error_messages)

@app.route('/query_uql', methods=['POST'])
def query_uql():
    data = request.get_json(force=True)
    user_query = data.get('query')
    while True:
        uql_query, uql_prompt = text_to_uql(user_query)
        errors, corrected_uql, has_errors = validate_uql_response(uql_query)
        if has_errors:
            logging.error("Errors detected: %s", errors)
            final_uql_query = get_reflection_for_uql(uql_prompt, corrected_uql, errors)
            user_query = final_uql_query  
        else:
            logging.info("No errors found, returning valid UQL.")
            return jsonify({"response": corrected_uql})

if __name__ == '__main__':
    app.run(debug=True)