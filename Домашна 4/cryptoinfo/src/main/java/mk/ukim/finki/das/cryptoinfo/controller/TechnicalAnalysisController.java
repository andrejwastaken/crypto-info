package mk.ukim.finki.das.cryptoinfo.controller;

import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysis;
import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysisTimePeriod;
import mk.ukim.finki.das.cryptoinfo.service.TechnicalAnalysisService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/ta")
@RequiredArgsConstructor
public class TechnicalAnalysisController {
    private final TechnicalAnalysisService technicalAnalysisService;

    @GetMapping("/{symbol}/score")
    public ResponseEntity<Double> getScoreForSymbol(
            @PathVariable @NotNull String symbol,
            @RequestParam TechnicalAnalysisTimePeriod period){
        Double scoreForSymbol = technicalAnalysisService.getScoreForSymbol(symbol, period);
        if (scoreForSymbol == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(scoreForSymbol);
    }

    @GetMapping("/{symbol}")
    public ResponseEntity<List<TechnicalAnalysis>> getDataForSymbol(
            @PathVariable @NotNull String symbol){
        List<TechnicalAnalysis> data = technicalAnalysisService.getStatsForSymbol(symbol);
        if (data == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(data);
    }
}
