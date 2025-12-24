package mk.ukim.finki.das.cryptoinfo.controller;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PagedResourcesAssembler;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.PagedModel;
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
    private final PagedResourcesAssembler<TextSentiment> assembler;

    @SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection")
    public TextSentimentController(TextSentimentService textSentimentService, PagedResourcesAssembler<TextSentiment> assembler) {
        this.textSentimentService = textSentimentService;
        this.assembler = assembler;
    }

    @GetMapping
    public PagedModel<EntityModel<TextSentiment>> getNewsBySymbol(
            @RequestParam String symbol,
            Pageable pageable
    ){
        Page<TextSentiment> page = textSentimentService.getNewsBySymbol(symbol, pageable);
        return assembler.toModel(page);
    }
}
