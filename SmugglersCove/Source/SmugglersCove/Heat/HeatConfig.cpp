// Copyright Epic Games, Inc. All Rights Reserved.

#include "HeatConfig.h"

namespace
{
	float NavyRepAlpha(float NavyReputation)
	{
		// Map [-1, +1] onto [0, 1] for interpolation.
		return (FMath::Clamp(NavyReputation, -1.0f, 1.0f) + 1.0f) * 0.5f;
	}
}

float UHeatConfig::GetNavyGainMultiplier(float NavyReputation) const
{
	return FMath::Lerp(GainMultiplierAtMinNavyRep, GainMultiplierAtMaxNavyRep, NavyRepAlpha(NavyReputation));
}

float UHeatConfig::GetNavyDecayMultiplier(float NavyReputation) const
{
	return FMath::Lerp(DecayMultiplierAtMinNavyRep, DecayMultiplierAtMaxNavyRep, NavyRepAlpha(NavyReputation));
}
