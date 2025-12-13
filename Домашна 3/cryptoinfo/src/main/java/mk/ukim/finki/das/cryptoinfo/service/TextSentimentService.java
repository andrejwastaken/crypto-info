package mk.ukim.finki.das.cryptoinfo.service;

import mk.ukim.finki.das.cryptoinfo.model.TextSentiment;
import mk.ukim.finki.das.cryptoinfo.repository.TextSentimentRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TextSentimentService {
    private final TextSentimentRepository textSentimentRepository;

    public TextSentimentService(TextSentimentRepository textSentimentRepository) {
        this.textSentimentRepository = textSentimentRepository;
    }

    public List<TextSentiment> getAll(){
        return textSentimentRepository.findAll();
    }

    public Page<TextSentiment> getNewsBySymbol(String symbol, Pageable pageable){
        return textSentimentRepository.findTopBySymbolPriority(symbol, pageable);
    }


}
