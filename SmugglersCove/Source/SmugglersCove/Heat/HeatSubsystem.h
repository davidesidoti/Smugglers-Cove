// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "HeatTypes.h"
#include "HeatNavyReputationProvider.h"
#include "HeatSubsystem.generated.h"

class UHeatConfig;

/**
 * Owner of all Heat state: global notoriety plus per-activity localized Heat.
 * Pure model — knows nothing about UI, inspections or the world. Time is advanced
 * explicitly via AdvanceTime by whoever owns the game clock, so the system stays
 * deterministic and unit-testable.
 */
UCLASS()
class SMUGGLERSCOVE_API UHeatSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	// --- Setup / injection ---

	/** Sets the tunables. Until called, the UHeatConfig class defaults are used. */
	UFUNCTION(BlueprintCallable, Category = "Heat")
	void SetConfig(UHeatConfig* InConfig);

	/** Injects the source of Navy reputation (the future faction system, or a test mock). */
	UFUNCTION(BlueprintCallable, Category = "Heat")
	void SetNavyReputationProvider(TScriptInterface<IHeatNavyReputationProvider> InProvider);

	/** Fallback Navy reputation in [-1, +1], used only when no provider is injected. */
	UFUNCTION(BlueprintCallable, Category = "Heat")
	void SetFallbackNavyReputation(float InNavyReputation);

	/** Registers an activity (business) so it tracks its own localized Heat, starting at 0. */
	UFUNCTION(BlueprintCallable, Category = "Heat")
	void RegisterActivity(FName Activity);

	UFUNCTION(BlueprintPure, Category = "Heat")
	bool IsActivityRegistered(FName Activity) const;

	UFUNCTION(BlueprintPure, Category = "Heat")
	TArray<FName> GetRegisteredActivities() const;

	// --- Operations ---

	/**
	 * Applies an illicit action: raises the activity's Heat by the modulated gain
	 * (discretion, witnesses, Navy presence, Navy reputation) and bleeds a configured
	 * fraction into global Heat. Returns the gain applied to the activity.
	 */
	UFUNCTION(BlueprintCallable, Category = "Heat")
	float ApplyIllicitAction(const FHeatActionContext& Context);

	/**
	 * Applies a legal action (serving legal ships, supplying the Navy, donations):
	 * cools the activity's Heat by CleaningPower * LegalCoolingMultiplier and bleeds
	 * the configured fraction of that cooling into global Heat.
	 */
	UFUNCTION(BlueprintCallable, Category = "Heat")
	void ApplyLegalAction(FName Activity, float CleaningPower);

	/** Advances time by GameHours, applying passive decay modulated by Navy reputation. */
	UFUNCTION(BlueprintCallable, Category = "Heat")
	void AdvanceTime(float GameHours);

	// --- Queries ---

	UFUNCTION(BlueprintPure, Category = "Heat")
	float GetGlobalHeat() const { return GlobalHeat; }

	/** Global Heat as [0, 1] of MaxHeat — handy for UI bars and inspection-frequency curves. */
	UFUNCTION(BlueprintPure, Category = "Heat")
	float GetGlobalHeatNormalized() const;

	UFUNCTION(BlueprintPure, Category = "Heat")
	float GetActivityHeat(FName Activity) const;

	UFUNCTION(BlueprintPure, Category = "Heat")
	float GetActivityHeatNormalized(FName Activity) const;

	/** Current Navy reputation in [-1, +1], from the provider if injected, else the fallback. */
	UFUNCTION(BlueprintPure, Category = "Heat")
	float GetNavyReputation() const;

	// --- Events (presentation observes; the model never calls out) ---

	UPROPERTY(BlueprintAssignable, Category = "Heat")
	FOnGlobalHeatChanged OnGlobalHeatChanged;

	UPROPERTY(BlueprintAssignable, Category = "Heat")
	FOnActivityHeatChanged OnActivityHeatChanged;

private:
	const UHeatConfig* GetConfigOrDefault() const;
	void SetGlobalHeatInternal(float NewValue);
	void SetActivityHeatInternal(FName Activity, float NewValue);
	/** Returns the map entry for Activity, registering it (with a log) if gameplay never did. */
	float& FindOrRegisterActivity(FName Activity);

	UPROPERTY()
	TObjectPtr<UHeatConfig> Config;

	UPROPERTY()
	TScriptInterface<IHeatNavyReputationProvider> NavyReputationProvider;

	float FallbackNavyReputation = 0.0f;

	float GlobalHeat = 0.0f;

	TMap<FName, float> ActivityHeat;
};
