// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "HeatConfig.generated.h"

/**
 * All Heat-system tunables, exposed as a data asset so designers can balance without touching code.
 * Navy reputation is normalized to [-1, +1] everywhere: -1 = hostile, 0 = neutral, +1 = trusted.
 * With the default symmetric multipliers, neutral reputation yields exactly 1.0 (no modulation).
 */
UCLASS(BlueprintType)
class SMUGGLERSCOVE_API UHeatConfig : public UDataAsset
{
	GENERATED_BODY()

public:
	/** Global and per-activity Heat are clamped to [0, MaxHeat]. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Bounds", meta = (ClampMin = "1.0"))
	float MaxHeat = 100.0f;

	/** Passive decay of global Heat per game hour, before Navy-reputation modulation. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Decay", meta = (ClampMin = "0.0"))
	float GlobalDecayPerHour = 0.5f;

	/** Passive decay of each activity's Heat per game hour, before Navy-reputation modulation. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Decay", meta = (ClampMin = "0.0"))
	float ActivityDecayPerHour = 1.0f;

	/** Fraction of an illicit action's modulated gain that also raises global Heat (and of legal cooling that also lowers it). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Gain", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float GlobalBleedFraction = 0.5f;

	/** Multiplier applied to a legal action's CleaningPower when reducing the activity's Heat. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Cooling", meta = (ClampMin = "0.0"))
	float LegalCoolingMultiplier = 1.0f;

	/** Gain reduction at full discretion: gain *= 1 - Discretion * this. 0.75 means a fully discreet deal generates 25% of the Heat. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Modulation", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float MaxDiscretionGainReduction = 0.75f;

	/** Extra gain per witness: gain *= 1 + WitnessCount * this. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Modulation", meta = (ClampMin = "0.0"))
	float WitnessGainPerWitness = 0.15f;

	/** Gain multiplier when a Navy ship is docked/nearby during the action. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Modulation", meta = (ClampMin = "1.0"))
	float NavyShipNearbyMultiplier = 2.0f;

	/** Heat-gain multiplier at Navy reputation -1 (hostile). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Navy Reputation", meta = (ClampMin = "0.0"))
	float GainMultiplierAtMinNavyRep = 1.5f;

	/** Heat-gain multiplier at Navy reputation +1 (trusted). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Navy Reputation", meta = (ClampMin = "0.0"))
	float GainMultiplierAtMaxNavyRep = 0.5f;

	/** Decay multiplier at Navy reputation -1 (hostile): low rep cools slowly. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Navy Reputation", meta = (ClampMin = "0.0"))
	float DecayMultiplierAtMinNavyRep = 0.5f;

	/** Decay multiplier at Navy reputation +1 (trusted): high rep cools fast. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heat|Navy Reputation", meta = (ClampMin = "0.0"))
	float DecayMultiplierAtMaxNavyRep = 1.5f;

	/** Heat-gain multiplier for a given Navy reputation in [-1, +1]. */
	UFUNCTION(BlueprintPure, Category = "Heat")
	float GetNavyGainMultiplier(float NavyReputation) const;

	/** Heat-decay multiplier for a given Navy reputation in [-1, +1]. */
	UFUNCTION(BlueprintPure, Category = "Heat")
	float GetNavyDecayMultiplier(float NavyReputation) const;
};
