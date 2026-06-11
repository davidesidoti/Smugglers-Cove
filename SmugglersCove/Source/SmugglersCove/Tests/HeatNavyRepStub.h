// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Heat/HeatNavyReputationProvider.h"
#include "HeatNavyRepStub.generated.h"

/** Test-only stand-in for the future faction system: returns a settable Navy reputation. */
UCLASS()
class UHeatNavyRepStub : public UObject, public IHeatNavyReputationProvider
{
	GENERATED_BODY()

public:
	float NavyReputation = 0.0f;

	virtual float GetNavyReputation_Implementation() override { return NavyReputation; }
};
