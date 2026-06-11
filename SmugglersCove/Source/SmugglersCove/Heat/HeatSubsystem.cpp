// Copyright Epic Games, Inc. All Rights Reserved.

#include "HeatSubsystem.h"
#include "HeatConfig.h"
#include "SmugglersCove.h"

void UHeatSubsystem::SetConfig(UHeatConfig* InConfig)
{
	Config = InConfig;
}

void UHeatSubsystem::SetNavyReputationProvider(TScriptInterface<IHeatNavyReputationProvider> InProvider)
{
	NavyReputationProvider = InProvider;
}

void UHeatSubsystem::SetFallbackNavyReputation(float InNavyReputation)
{
	FallbackNavyReputation = FMath::Clamp(InNavyReputation, -1.0f, 1.0f);
}

void UHeatSubsystem::RegisterActivity(FName Activity)
{
	if (Activity.IsNone())
	{
		UE_LOG(LogSmugglersCove, Warning, TEXT("HeatSubsystem: cannot register activity with name None"));
		return;
	}
	ActivityHeat.FindOrAdd(Activity, 0.0f);
}

bool UHeatSubsystem::IsActivityRegistered(FName Activity) const
{
	return ActivityHeat.Contains(Activity);
}

TArray<FName> UHeatSubsystem::GetRegisteredActivities() const
{
	TArray<FName> Activities;
	ActivityHeat.GenerateKeyArray(Activities);
	return Activities;
}

float UHeatSubsystem::ApplyIllicitAction(const FHeatActionContext& Context)
{
	const UHeatConfig* Cfg = GetConfigOrDefault();

	float Gain = FMath::Max(Context.BaseSeverity, 0.0f);
	Gain *= 1.0f - FMath::Clamp(Context.Discretion, 0.0f, 1.0f) * Cfg->MaxDiscretionGainReduction;
	Gain *= 1.0f + FMath::Max(Context.WitnessCount, 0) * Cfg->WitnessGainPerWitness;
	if (Context.bNavyShipNearby)
	{
		Gain *= Cfg->NavyShipNearbyMultiplier;
	}
	Gain *= Cfg->GetNavyGainMultiplier(GetNavyReputation());

	if (Gain <= 0.0f)
	{
		return 0.0f;
	}

	const float Current = FindOrRegisterActivity(Context.Activity);
	SetActivityHeatInternal(Context.Activity, Current + Gain);
	SetGlobalHeatInternal(GlobalHeat + Gain * Cfg->GlobalBleedFraction);
	return Gain;
}

void UHeatSubsystem::ApplyLegalAction(FName Activity, float CleaningPower)
{
	const UHeatConfig* Cfg = GetConfigOrDefault();

	const float Cooling = FMath::Max(CleaningPower, 0.0f) * Cfg->LegalCoolingMultiplier;
	if (Cooling <= 0.0f)
	{
		return;
	}

	const float Current = FindOrRegisterActivity(Activity);
	SetActivityHeatInternal(Activity, Current - Cooling);
	SetGlobalHeatInternal(GlobalHeat - Cooling * Cfg->GlobalBleedFraction);
}

void UHeatSubsystem::AdvanceTime(float GameHours)
{
	if (GameHours <= 0.0f)
	{
		return;
	}

	const UHeatConfig* Cfg = GetConfigOrDefault();
	const float DecayMultiplier = Cfg->GetNavyDecayMultiplier(GetNavyReputation());

	SetGlobalHeatInternal(GlobalHeat - Cfg->GlobalDecayPerHour * GameHours * DecayMultiplier);

	// Iterate a copy of the keys: OnActivityHeatChanged handlers may register activities,
	// which would invalidate a live map iterator.
	const float ActivityDecay = Cfg->ActivityDecayPerHour * GameHours * DecayMultiplier;
	TArray<FName> Activities;
	ActivityHeat.GenerateKeyArray(Activities);
	for (const FName& Activity : Activities)
	{
		SetActivityHeatInternal(Activity, ActivityHeat.FindChecked(Activity) - ActivityDecay);
	}

	// Decay first, then pressure: the hour you just lived counts at its end-of-hour heat.
	TickInspection(GameHours);
}

void UHeatSubsystem::SetInspectionSeed(int32 Seed)
{
	InspectionRandom.Initialize(Seed);
}

void UHeatSubsystem::ResolvePendingInspection()
{
	PendingInspection = FPendingInspection();
}

void UHeatSubsystem::ForceScheduleInspection(FName TargetActivity)
{
	if (PendingInspection.bValid)
	{
		UE_LOG(LogSmugglersCove, Warning, TEXT("HeatSubsystem: an inspection is already pending — resolve it before forcing another"));
		return;
	}
	ScheduleInspectionInternal(TargetActivity.IsNone() ? PickInspectionTarget() : TargetActivity);
}

float UHeatSubsystem::GetInspectionPressureNormalized() const
{
	const UHeatConfig* Cfg = GetConfigOrDefault();
	return Cfg->InspectionPressureThreshold > 0.0f
		? FMath::Clamp(InspectionPressure / Cfg->InspectionPressureThreshold, 0.0f, 1.0f)
		: 0.0f;
}

void UHeatSubsystem::TickInspection(float GameHours)
{
	const UHeatConfig* Cfg = GetConfigOrDefault();

	if (PendingInspection.bValid)
	{
		// Pressure is paused while an inspection is pending; only the warning counts down.
		if (!PendingInspection.bDue)
		{
			PendingInspection.HoursUntilDue = FMath::Max(PendingInspection.HoursUntilDue - GameHours, 0.0f);
			if (PendingInspection.HoursUntilDue <= 0.0f)
			{
				MarkInspectionDue();
			}
		}
		return;
	}

	const float Rate = Cfg->InspectionPressurePerHour
		* GetGlobalHeatNormalized()
		* Cfg->GetNavyPressureMultiplier(GetNavyReputation());
	if (Rate <= 0.0f)
	{
		return;
	}

	InspectionPressure += Rate * GameHours;
	if (InspectionPressure >= Cfg->InspectionPressureThreshold)
	{
		ScheduleInspectionInternal(PickInspectionTarget());
	}
}

void UHeatSubsystem::ScheduleInspectionInternal(FName TargetActivity)
{
	const UHeatConfig* Cfg = GetConfigOrDefault();

	InspectionPressure = 0.0f;

	FPendingInspection Inspection;
	Inspection.bValid = true;
	Inspection.TargetActivity = TargetActivity;
	Inspection.TargetActivityHeat = GetActivityHeat(TargetActivity);

	float Warning = Cfg->GetWarningHours(GetNavyReputation());
	if (Cfg->WarningJitterHours > 0.0f)
	{
		Warning += InspectionRandom.FRandRange(-Cfg->WarningJitterHours, Cfg->WarningJitterHours);
	}
	Inspection.WarningHours = FMath::Max(Warning, 0.0f);
	Inspection.HoursUntilDue = Inspection.WarningHours;

	PendingInspection = Inspection;
	OnInspectionScheduled.Broadcast(PendingInspection);

	// No warning at all = a surprise inspection: the inspector is already at the door.
	if (PendingInspection.HoursUntilDue <= 0.0f)
	{
		MarkInspectionDue();
	}
}

void UHeatSubsystem::MarkInspectionDue()
{
	PendingInspection.bDue = true;
	OnInspectionDue.Broadcast(PendingInspection);
}

FName UHeatSubsystem::PickInspectionTarget() const
{
	FName Best;
	float BestHeat = -1.0f;
	for (const TPair<FName, float>& Pair : ActivityHeat)
	{
		const bool bHotter = Pair.Value > BestHeat;
		const bool bTieBrokenByName = Pair.Value == BestHeat && Pair.Key.LexicalLess(Best);
		if (bHotter || bTieBrokenByName)
		{
			Best = Pair.Key;
			BestHeat = Pair.Value;
		}
	}
	return Best;
}

float UHeatSubsystem::GetGlobalHeatNormalized() const
{
	const UHeatConfig* Cfg = GetConfigOrDefault();
	return Cfg->MaxHeat > 0.0f ? GlobalHeat / Cfg->MaxHeat : 0.0f;
}

float UHeatSubsystem::GetActivityHeat(FName Activity) const
{
	if (const float* Found = ActivityHeat.Find(Activity))
	{
		return *Found;
	}
	return 0.0f;
}

float UHeatSubsystem::GetActivityHeatNormalized(FName Activity) const
{
	const UHeatConfig* Cfg = GetConfigOrDefault();
	return Cfg->MaxHeat > 0.0f ? GetActivityHeat(Activity) / Cfg->MaxHeat : 0.0f;
}

float UHeatSubsystem::GetNavyReputation() const
{
	if (NavyReputationProvider.GetObject() != nullptr)
	{
		const float Rep = IHeatNavyReputationProvider::Execute_GetNavyReputation(NavyReputationProvider.GetObject());
		return FMath::Clamp(Rep, -1.0f, 1.0f);
	}
	return FallbackNavyReputation;
}

const UHeatConfig* UHeatSubsystem::GetConfigOrDefault() const
{
	return Config ? Config.Get() : GetDefault<UHeatConfig>();
}

void UHeatSubsystem::SetGlobalHeatInternal(float NewValue)
{
	const float Clamped = FMath::Clamp(NewValue, 0.0f, GetConfigOrDefault()->MaxHeat);
	if (!FMath::IsNearlyEqual(Clamped, GlobalHeat))
	{
		GlobalHeat = Clamped;
		OnGlobalHeatChanged.Broadcast(GlobalHeat);
	}
}

void UHeatSubsystem::SetActivityHeatInternal(FName Activity, float NewValue)
{
	float& Stored = ActivityHeat.FindChecked(Activity);
	const float Clamped = FMath::Clamp(NewValue, 0.0f, GetConfigOrDefault()->MaxHeat);
	if (!FMath::IsNearlyEqual(Clamped, Stored))
	{
		Stored = Clamped;
		OnActivityHeatChanged.Broadcast(Activity, Stored);
	}
}

float& UHeatSubsystem::FindOrRegisterActivity(FName Activity)
{
	if (float* Found = ActivityHeat.Find(Activity))
	{
		return *Found;
	}
	UE_LOG(LogSmugglersCove, Log, TEXT("HeatSubsystem: activity '%s' was not registered — registering on first use"), *Activity.ToString());
	return ActivityHeat.Add(Activity, 0.0f);
}
