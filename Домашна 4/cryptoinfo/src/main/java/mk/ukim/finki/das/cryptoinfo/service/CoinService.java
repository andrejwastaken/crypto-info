package mk.ukim.finki.das.cryptoinfo.service;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.Coin;
import mk.ukim.finki.das.cryptoinfo.repository.CoinRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CoinService {
    private final CoinRepository coinRepository;

    public List<Coin> getCoins(){
        return coinRepository.findAll();
    }
}
