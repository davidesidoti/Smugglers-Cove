// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "HeatNavyReputationProvider.generated.h"

UINTERFACE(MinimalAPI, Blueprintable)
class UHeatNavyReputationProvider : public UInterface
{
	GENERATED_BODY()
};

/**
 * Minimal seam toward the (not yet implemented) faction system.
 * Whoever owns Navy reputation implements this; the Heat subsystem only reads through it.
 */
class SMUGGLERSCOVE_API IHeatNavyReputationProvider
{
	GENERATED_BODY()

public:
	/** Navy reputation normalized to [-1, +1]: -1 = hostile, 0 = neutral, +1 = trusted. */
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Heat")
	float GetNavyReputation();
};
