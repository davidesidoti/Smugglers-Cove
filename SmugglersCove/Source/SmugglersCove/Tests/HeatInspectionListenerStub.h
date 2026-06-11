// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Heat/HeatInspectionTypes.h"
#include "HeatInspectionListenerStub.generated.h"

/** Test-only listener that counts inspection events and captures their payloads. */
UCLASS()
class UHeatInspectionListenerStub : public UObject
{
	GENERATED_BODY()

public:
	int32 ScheduledCount = 0;
	int32 DueCount = 0;
	FPendingInspection LastScheduled;
	FPendingInspection LastDue;

	UFUNCTION()
	void HandleScheduled(const FPendingInspection& Inspection) { ++ScheduledCount; LastScheduled = Inspection; }

	UFUNCTION()
	void HandleDue(const FPendingInspection& Inspection) { ++DueCount; LastDue = Inspection; }
};
