// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "HeatTypes.generated.h"

/**
 * Describes a single illicit action for Heat purposes.
 * Built by gameplay (Blueprint or C++) and passed to UHeatSubsystem::ApplyIllicitAction.
 */
USTRUCT(BlueprintType)
struct FHeatActionContext
{
	GENERATED_BODY()

	/** Activity (business) where the action happened. Should be registered with the Heat subsystem. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Heat")
	FName Activity;

	/** Heat the action generates before any modulation (discretion, witnesses, Navy reputation). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Heat", meta = (ClampMin = "0.0"))
	float BaseSeverity = 0.0f;

	/** 0 = fully exposed (broad daylight, open spot, goods on display), 1 = fully discreet (night, hidden, little exposed). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Heat", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float Discretion = 0.0f;

	/** Number of witnesses to the action. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Heat", meta = (ClampMin = "0"))
	int32 WitnessCount = 0;

	/** True if a Navy ship is docked or patrolling nearby — spikes the generated Heat. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Heat")
	bool bNavyShipNearby = false;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnGlobalHeatChanged, float, NewGlobalHeat);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnActivityHeatChanged, FName, Activity, float, NewHeat);
