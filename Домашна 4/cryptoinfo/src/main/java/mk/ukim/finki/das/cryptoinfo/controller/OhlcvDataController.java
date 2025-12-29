package mk.ukim.finki.das.cryptoinfo.controller;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.dto.CoinStatsDTO;
import mk.ukim.finki.das.cryptoinfo.model.CoinPctChangeProjection;
import mk.ukim.finki.das.cryptoinfo.model.OhlcvData;
import mk.ukim.finki.das.cryptoinfo.service.OhlcvDataService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.data.web.PagedResourcesAssembler;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.PagedModel;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.http.HttpResponse;
import java.util.List;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/ohlcv-data")
@RequiredArgsConstructor
public class OhlcvDataController {
    private final OhlcvDataService ohlcvDataService;
    @SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection") // bez ova dava error vo intellij ama raboti
    private final PagedResourcesAssembler<OhlcvData> assembler;

    @GetMapping("/{symbol}")
    public PagedModel<EntityModel<OhlcvData>> getCoinData(
            @PathVariable String symbol,
            @PageableDefault(sort = "date", size = 30, direction = Sort.Direction.DESC)
            Pageable pageable
    ){
        Page<OhlcvData> page = ohlcvDataService.getDataForSymbol(symbol.toUpperCase(), pageable);
        return assembler.toModel(page);
    }
    
    @GetMapping("/{symbol}/stats")
    public ResponseEntity<CoinStatsDTO> getCoinStats(@PathVariable String symbol) {
        CoinStatsDTO stats = ohlcvDataService.getCoinStats(symbol.toUpperCase());
        if (stats == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(stats);
    }

    @GetMapping("/carousel")
    public ResponseEntity<List<CoinPctChangeProjection>> getCarouselData(){
        return ResponseEntity.ok(ohlcvDataService.getTopCoinsWithPctChange());
    }
}
