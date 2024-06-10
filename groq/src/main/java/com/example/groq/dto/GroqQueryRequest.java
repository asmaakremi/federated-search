package com.example.groq.dto;


public class GroqQueryRequest {
    private String query;

    public GroqQueryRequest() {
    }
    public GroqQueryRequest(String query, String rdf_model) {
        this.query = query;
    }

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }


    @Override
    public String toString() {
        return "GroqRequest{" +
                "query='" + query + '\'' +
                '}';
    }
}


