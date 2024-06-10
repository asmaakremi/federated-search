from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "https://vdevpril922dsy.dsone.3ds.com:444"]) 

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
        "user": "string",
        "response_format": {
            "type": "text", 
            "temperature": 0.7
        }
    }
    logging.debug(f"Sending request to {url} with payload: {payload} and headers: {headers}")

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        generated_response = response.json()['choices'][0]['message']['content'].strip()
        return generated_response
    else:
        return f"Failed to generate response. Status code: {response.status_code}\nResponse: {response.text}"

    
def text_to_uql(query):
    prompt = f"""
You are an expert in transforming natural language queries into UQL queries using the given ontology .based on user questions about data stored in an RDF graph, use the given ontology and documentation to understand the UQL syntax, rules, and ontology, and then generate only the UQL query equivalent for the given natural language query without explanation and without any added text except the UQL query.

### UQL Documentation ###

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
   - dos_bucket: Pass a DOS bucket for all DOS checkouts.
   - fcs_url_mode: Choose between ‘DIRECT’ and ‘REDIRECT’ modes for FCS checkouts.
   - with_Idx_Search: Ignore the searchable property if true.
   - with_relationship_search: Include relationships in the search if true.

4. **Label Parameter**:
   - A query must include a label parameter in JSON format, such as $ApplicationName-$User-$Timestamp.

5. **Order Field**:
   - Defines the sort criterion. Less than 1000 objects: sort on any predicates. More than 1000 objects: sort on specific attributes like relevance, ds6w:modified, ds6w:created, ds6w:responsible, ds6w:label.

  
** RDF Model **
 Ontology:
 @prefix vpmReference: <http://www.3ds.com/RDF/ontology/archetype/vpmReference#> .
 @prefix physicalProduct: <http://www.3ds.com/RDF/ontology/universe/physicalProduct#> .
 @prefix product: <http://www.3ds.com/RDF/ontology/universe/product#> .
 @prefix archetype: <http://www.3ds.com/RDF/ontology/archetype#> .
 @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
 @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
 @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
 @prefix owl: <http://www.w3.org/2002/07/owl#> .
 @prefix prov: <http://www.w3.org/ns/prov#> .
 @prefix dsqt: <http://www.3ds.com/RDF/Corpus/dsqt/> .

 vpmReference: a owl:Ontology ;
     rdfs:comment "Physical Product archetype"@en .

 vpmReference rdf:type owl:Class ;
     rdfs:subClassOf archetype:Archetype .

 physicalProduct:PhysicalProduct owl:equivalentClass vpmReference .
 product:Product owl:equivalentClass vpmReference .

 ds6w:type a owl:DatatypeProperty;
     rdfs:label "Type"@en;
     rdfs:comment "The type of 3DSpace object"@en;
     rdfs:domain vpmReference;
     rdfs:range xsd:string.

 ds6w:modified a owl:DatatypeProperty;
     rdfs:label "Modified"@en;
     rdfs:comment "The date and time when the VPM Reference was last modified."@en;
     rdfs:domain vpmReference;
     prov:hadPrimarySource "3dspace";
     rdfs:range xsd:dateTime.

ds6w:created a owl:DatatypeProperty;
        rdfs:label "Created"@en;
        rdfs:comment "The date and time when the VPM Reference was created."@en;
        rdfs:domain vpmReference;
        prov:hadPrimarySource "3dspace";
        rdfs:range xsd:dateTime.

 RDF Model Details:
    - 'ds6w:created' represents the creation date.
    - 'ds6w:modified' represents the modification date.
    - 'rdf:type' specifies the type of object within the VPMReference class hierarchy.
    - 'ds6w:type' with a value 'VPMReference' indicates filtering by specific types.
    - 'physicalProduct:PhysicalProduct' and 'product:Product' are equivalent to 'vpmReference:VPMReference' which is the Type .

6. **Examples**:

   - Example 1:
     - Natural Language: give me physical products that are created between 2024-05-01 to 2024-05-28
     - UQL: [ds6w:created]>="2024-05-01T00:00:00.000Z" AND [ds6w:created]<="2024-05-28T23:59:59.000Z" AND [ds6w:type]:"VPMReference"
  
   - Example 2:
     - Natural Language: give me products with type vpmReference that are created this month by me : ODT ITP
     - UQL: ([ds6w:modified]>="2024-04-30T22:00:00.000Z" AND [ds6w:modified]<="2024-05-31T21:59:59.000Z") AND (([ds6w:lastModifiedBy]:"ODT ITP" OR [ds6w:responsible]:"ODT ITP") AND [ds6w:type]:"VPMReference")

   - Example 3:
     - Natural Language: give me products that are created this month by me : ODT ITP
     - UQL: ([ds6w:modified]>="2024-04-30T22:00:00.000Z" AND [ds6w:modified]<="2024-05-31T21:59:59.000Z") AND (([ds6w:lastModifiedBy]:"ODT ITP" OR [ds6w:responsible]:"ODT ITP") AND [ds6w:type]:"VPMReference")

    - Example 4:
    - Natural Language:give me products modified by the user ODT IT 
    - UQL: [ds6w:responsible]:"ODT ITP" AND [ds6w:type]:"VPMReference"
    
    - Example 5:
    - Natural Language: give me all products
    - UQL: "flattenedtaxonomies:\"types/VPMReference\""

### Given the natural language query: "{query}", write a valid UQL query that accurately extracts or calculates the requested information from the RDF graph. When you find in the natural query: physical product , the type is VPMReference so the query must contain [ds6w:type]:"VPMReference". The output should not contain any special characters like \n, and without any explanations, just the UQL query.
"""
    try:
        return call_llm(prompt), prompt
    except Exception as e:
        return str(e) 

def get_reflection_for_uql(full_prompt ,llm_response):
    reflection_prompt = f"""
You were given the following prompt:

{full_prompt}

Your initial UQL conversion was:

{llm_response}

Please identify any errors in the conversion, focusing on these aspects:
1. SO IMPORTANT: Remove any additional text or explanation and keep ONLY the UQL QUERY. DO NOT ADD ANY TEXT.
2. All UQL fields must match the expected ds6w: prefixed fields.
3. Logical operators (AND, OR, NOT) must be correctly used.
4. Date and number formats must adhere to UQL requirements.
5. Ensure that all conditions and joins are appropriately represented.
6. 'physical Product', 'vpmReference' are all types of "VPMReference" so the UQL query MUST include "[ds6w:type]:"VPMReference"".

Example 1:
- Natural Language: search all products 
- Your response should be like this: [ds6w:type]:"VPMReference"

Example 2:
- Natural Language: give me products created this week
- Your response should be like this: [ds6w:modified]>="2024-05-26T22:00:00.000Z" AND [ds6w:modified]<="2024-07-03T21:59:59.000Z" AND [ds6w:type]:"VPMReference"

Example 3:
- Natural Language: show me physical products created this month 
- Your response should be like this: [ds6w:modified]>="2024-04-30T22:00:00.000Z" AND [ds6w:modified]<="2024-05-31T21:59:59.000Z" AND [ds6w:type]:"VPMReference"

Example 4:
- Natural Language: show me products created this month by the person responsible or named MCM OCDxComplianceUser
- Your response should be like this: ([ds6w:modified]>="2024-04-30T22:00:00.000Z" AND [ds6w:modified]<="2024-05-31T21:59:59.000Z") AND (([ds6w:lastModifiedBy]:"MCM OCDxComplianceUser" OR [ds6w:responsible]:"MCM OCDxComplianceUser")) AND [ds6w:type]:"VPMReference"

Example 5:
- Natural Language: search for all vpmreference
- Your response should be like this: [ds6w:type]:"VPMReference"

Rewrite the UQL response ensuring it adheres to these rules. Respond ONLY with the valid UQL query format AND SO IMPORTANT DO NOT ADD ANY EXTRA TEXT.
"""
    corrected_uql = call_llm(reflection_prompt)
    return corrected_uql

@app.route('/query_groq', methods=['POST'])
def query_groq():
    data = request.get_json(force=True)  
    user_query = data.get('query')
    print("User Query :", user_query)  
    uql_query, uql_prompt = text_to_uql(user_query)
    final_uql_query=get_reflection_for_uql(uql_prompt,uql_query)
    print("Final Query :", final_uql_query)  
    return jsonify({"response": final_uql_query})


if __name__ == "__main__":
    app.run(debug=True)
