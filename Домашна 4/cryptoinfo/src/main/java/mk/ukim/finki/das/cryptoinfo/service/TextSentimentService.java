package mk.ukim.finki.das.cryptoinfo.service;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.TextSentiment;
import mk.ukim.finki.das.cryptoinfo.repository.TextSentimentRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class TextSentimentService {
    private final TextSentimentRepository textSentimentRepository;

    public Page<TextSentiment> getNewsBySymbol(String symbol, Pageable pageable){
        return textSentimentRepository.findTopBySymbolPriority(symbol, pageable);
    }


}
