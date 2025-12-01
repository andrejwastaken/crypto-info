package mk.ukim.finki.das.cryptoinfo.controller;

import jakarta.websocket.server.PathParam;
import mk.ukim.finki.das.cryptoinfo.dto.CoinStatsDTO;
import mk.ukim.finki.das.cryptoinfo.model.OhlcvData;
import mk.ukim.finki.das.cryptoinfo.service.OhlcvDataService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.data.web.PagedResourcesAssembler;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.PagedModel;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/ohlcv-data")
public class OhlcvDataController {
    private final OhlcvDataService ohlcvDataService;
    private final PagedResourcesAssembler<OhlcvData> assembler;

    @SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection") // bez ova dava error vo intellij ama raboti
    public OhlcvDataController(OhlcvDataService ohlcvDataService, PagedResourcesAssembler<OhlcvData> assembler) {
        this.ohlcvDataService = ohlcvDataService;
        this.assembler = assembler;
    }

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

    @GetMapping("/date/{date}")
    public PagedModel<EntityModel<OhlcvData>> getTopCoinsData(
            @PathVariable LocalDate date,
            @PageableDefault(sort = "volume", direction = Sort.Direction.DESC)
            Pageable pageable
    ){
        if (date.isEqual(LocalDate.now())) date = date.minusDays(1);
        Page<OhlcvData> page = ohlcvDataService.getByDate(date, pageable);
        return assembler.toModel(page);
    }
}
