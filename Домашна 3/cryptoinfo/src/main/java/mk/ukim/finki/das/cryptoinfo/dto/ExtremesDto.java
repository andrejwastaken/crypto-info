package mk.ukim.finki.das.cryptoinfo.dto;

import mk.ukim.finki.das.cryptoinfo.model.OhlcvPrediction;

import java.util.List;

public record ExtremesDto (
        List<OhlcvPrediction> top,
        List<OhlcvPrediction> bottom
){}
