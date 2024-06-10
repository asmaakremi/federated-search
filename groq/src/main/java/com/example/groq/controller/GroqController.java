package com.example.groq.controller;

import com.example.groq.dto.GroqQueryRequest;
import com.example.groq.service.GroqService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.CrossOrigin;

@RestController

public class GroqController {
    @Autowired
    private GroqService groqService;
    @CrossOrigin(origins = "https://vdevpril922dsy.dsone.3ds.com:444")
    @PostMapping("/query")
    public ResponseEntity<String> handleQuery(@RequestBody GroqQueryRequest request) {
        try {
            String response = groqService.queryGroq(request.getQuery());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Failed to process the query: " + e.getMessage());
        }
    }

}
