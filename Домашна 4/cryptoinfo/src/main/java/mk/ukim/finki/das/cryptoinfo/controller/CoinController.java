package mk.ukim.finki.das.cryptoinfo.controller;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.Coin;
import mk.ukim.finki.das.cryptoinfo.service.CoinService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/coins")
@RequiredArgsConstructor
public class CoinController {
    private final CoinService coinService;

    @GetMapping("")
    public ResponseEntity<List<Coin>> getCoinAll(){
        List<Coin> coins = coinService.getCoins();
        return ResponseEntity.ok(coins);
    }

}
