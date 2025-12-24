package mk.ukim.finki.das.cryptoinfo.controller;

import mk.ukim.finki.das.cryptoinfo.dto.ExtremesDTO;
import mk.ukim.finki.das.cryptoinfo.model.OhlcvPrediction;
import mk.ukim.finki.das.cryptoinfo.service.OhlcvPredictionService;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/prediction")
public class OhlcvPredictionController {
    private final OhlcvPredictionService ohlcvPredictionService;

    public OhlcvPredictionController(OhlcvPredictionService ohlcvPredictionService) {
        this.ohlcvPredictionService = ohlcvPredictionService;
    }

    @GetMapping("/{symbol}")
    public HttpEntity<OhlcvPrediction> getPredictionForSymbol(@PathVariable String symbol){

        OhlcvPrediction predictionForSymbol = ohlcvPredictionService.getPredictionForSymbol(symbol);
        if (predictionForSymbol == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(predictionForSymbol);
    }

    @GetMapping("/extremes")
    public HttpEntity<ExtremesDTO> getTopAndBottom5(){
        return ResponseEntity.ok(ohlcvPredictionService.getTopAndBottom5ByPercentageChange());
    }
}
