package mk.ukim.finki.das.cryptoinfo.controller;

import java.util.List;

import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import mk.ukim.finki.das.cryptoinfo.model.TextSentiment;
import mk.ukim.finki.das.cryptoinfo.service.TextSentimentService;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/sentiment")
public class TextSentimentController {
    private final TextSentimentService textSentimentService;

    public TextSentimentController(TextSentimentService textSentimentService) {
        this.textSentimentService = textSentimentService;
    }

    @GetMapping
    public HttpEntity<List<TextSentiment>> getNewsBySymbol(
            @RequestParam String symbol){
        return ResponseEntity.ok(textSentimentService.getNewsBySymbol(symbol));
    }
}
