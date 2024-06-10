package com.example.groq.service;

import com.example.groq.dto.GroqQueryRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

@Service
public class GroqService {
    @Autowired
    private RestTemplate restTemplate;

    public String queryGroq(String userQuery) {
        String url="http://flask-api:5000/query_groq";

        GroqQueryRequest request = new GroqQueryRequest();
        request.setQuery(userQuery);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set(HttpHeaders.CONTENT_ENCODING, "UTF-8");

        HttpEntity<GroqQueryRequest> entity = new HttpEntity<>(request, headers);
        System.out.println("Final request payload: " + entity.toString());

        ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
        return response.getBody();    }
}
