// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "HeatInspectionTypes.generated.h"

/**
 * An inspection that has been scheduled against the player.
 * Produced by UHeatSubsystem when inspection pressure crosses its threshold;
 * consumed by the (future) first-person inspection set piece.
 */
USTRUCT(BlueprintType)
struct FPendingInspection
{
	GENERATED_BODY()

	/** Activity the inspector will target — the one with the highest localized Heat at schedule time. */
	UPROPERTY(BlueprintReadOnly, Category = "Heat|Inspection")
	FName TargetActivity;

	/** Total advance warning granted at schedule time (high Navy rep = long, hostile = none). */
	UPROPERTY(BlueprintReadOnly, Category = "Heat|Inspection")
	float WarningHours = 0.0f;

	/** Game hours left before the inspector arrives. Counts down via AdvanceTime. */
	UPROPERTY(BlueprintReadOnly, Category = "Heat|Inspection")
	float HoursUntilDue = 0.0f;

	/** The target activity's Heat when the inspection was scheduled — how incriminated you looked. */
	UPROPERTY(BlueprintReadOnly, Category = "Heat|Inspection")
	float TargetActivityHeat = 0.0f;

	/** True while this struct represents a real scheduled inspection. */
	UPROPERTY(BlueprintReadOnly, Category = "Heat|Inspection")
	bool bValid = false;

	/** True once the warning has elapsed: the inspector is on site, the set piece should run. */
	UPROPERTY(BlueprintReadOnly, Category = "Heat|Inspection")
	bool bDue = false;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnInspectionScheduled, const FPendingInspection&, Inspection);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnInspectionDue, const FPendingInspection&, Inspection);
